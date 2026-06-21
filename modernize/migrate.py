#!/usr/bin/env python3
"""migrate.py — 旧 custom_model_data リソースパックを 1.21.4+ の新アイテムモデル形式へ移行する。

背景:
  本番が配信する mitoujr.zip は 2021 cybozu オフィスパック（pack_format 7 / 1.17世代）。
  小麦の種・木のツルハシ・棒などのベースアイテムに `overrides` + `custom_model_data`
  predicate を載せて家具モデルを切り替える「旧オーバーライド方式」で作られている。
  ところが Paper 26.1.2（=1.21.4以降）でアイテムモデルが全面刷新され、
  item モデル JSON の `overrides`/`predicate`/`custom_model_data` は廃止、
  `assets/<ns>/items/<item>.json` の item definition（range_dispatch）に置き換わった。
  → 旧パックの CMD 駆動アイテムが軒並み素のベースアイテム見た目に戻る（＝「当たってない」）。

このスクリプトがやること:
  1. zip/ディレクトリを展開
  2. pack.mcmeta の pack_format を更新（+ supported_formats レンジで警告抑止）
  3. `models/item/*.json` のうち `overrides` を持つベースアイテムを検出
  4. その overrides（custom_model_data predicate）を `items/<base>.json` の
     range_dispatch エントリへ変換
  5. ベースモデル本体から `overrides` を除去（新版では無視される死蔵フィールド）
  6. 再 zip（ルートに assets/ が来る形）して sha1 を表示

  ★既存配置物（額縁内の wheat_seeds CMD=100 等）は、ワールド読込時に DataFixerUpper が
    旧 integer custom_model_data を新 component の floats[0] へ変換するため、
    range_dispatch（custom_model_data, 既定 index 0 = floats[0]）の threshold と整合する。
    つまり「パックを差し替えるだけ」で既存の家具も復活するはず（再配置不要）。

使い方:
  python3 migrate.py --in mitoujr.zip --out mitoujr-26.zip --pack-format 46
  python3 migrate.py --in ./extracted_pack/ --out mitoujr-26.zip --pack-format 46 --dry-run

pack_format の値:
  クライアント/サーバの版に対応する番号を渡す（1.21.4=46, 1.21.5=55, 1.21.6+=63〜 等）。
  正確な値は本番起動後のログ/`/version` で確認するのが確実。
  本スクリプトは supported_formats を [pack-format, 99] の広いレンジにして
  「古いパック」警告を抑止する（番号が多少ズレても機能ロードは効く）。
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile


def log(msg):
    print(msg, file=sys.stderr)


def normalize_model_ref(ref):
    """'item/foo' -> 'minecraft:item/foo'（名前空間を明示）。既に ':' があればそのまま。"""
    if ":" in ref:
        return ref
    return "minecraft:" + ref


def extract_source(src, work):
    """zip かディレクトリを work ディレクトリへ展開/コピーする。"""
    if os.path.isdir(src):
        shutil.copytree(src, work, dirs_exist_ok=True)
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            z.extractall(work)
    else:
        log(f"ERROR: {src} は zip でもディレクトリでもない")
        sys.exit(1)


def find_assets_root(work):
    """assets/ を含むルート（zip がフォルダごと圧縮された罠も吸収）を返す。"""
    if os.path.isdir(os.path.join(work, "assets")):
        return work
    # 1 階層ネストしている場合を救済
    for entry in os.listdir(work):
        p = os.path.join(work, entry)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "assets")):
            log(f"NOTE: assets/ が {entry}/ 配下にネスト。ルートを補正")
            return p
    log("ERROR: assets/ が見つからない")
    sys.exit(1)


def update_pack_mcmeta(root, pack_format):
    path = os.path.join(root, "pack.mcmeta")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {"pack": {}}
    pack = meta.setdefault("pack", {})
    old = pack.get("pack_format")
    pack["pack_format"] = pack_format
    # ★pack_format>64 では client が min_format/max_format を必須にする
    #   （無いと "missing mandatory fields min_format and max_format" でメタ読込失敗→
    #    fallback ロードになり items/ 定義が効かず家具が壊れる）。
    #   バニラ datapack に倣い min_format=[major,minor]（配列）, max_format=major（整数）。
    pack["min_format"] = [pack_format, 0]
    pack["max_format"] = pack_format
    pack.pop("supported_formats", None)  # 旧フィールドは format>64 では無効
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log(f"pack.mcmeta: pack_format {old} -> {pack_format} (min_format [{pack_format},0] / max_format {pack_format})")


def convert_overrides(root, dry_run):
    """models/item/*.json の overrides を items/<base>.json (range_dispatch) へ変換。"""
    ns_dir = os.path.join(root, "assets", "minecraft")
    models_item = os.path.join(ns_dir, "models", "item")
    items_dir = os.path.join(ns_dir, "items")
    if not os.path.isdir(models_item):
        log("ERROR: assets/minecraft/models/item/ が無い")
        sys.exit(1)

    converted, skipped_pred = [], []
    for fn in sorted(os.listdir(models_item)):
        if not fn.endswith(".json"):
            continue
        base = fn[:-5]
        mpath = os.path.join(models_item, fn)
        try:
            with open(mpath, encoding="utf-8") as f:
                model = json.load(f)
        except json.JSONDecodeError as e:
            log(f"WARN: {fn} パース失敗、スキップ ({e})")
            continue
        overrides = model.get("overrides")
        if not overrides:
            continue

        entries, skipped = [], []
        for ov in overrides:
            pred = ov.get("predicate", {})
            model_ref = ov.get("model")
            if list(pred.keys()) == ["custom_model_data"] and model_ref:
                entries.append({
                    "threshold": int(pred["custom_model_data"]),
                    "model": {"type": "minecraft:model", "model": normalize_model_ref(model_ref)},
                })
            else:
                # custom_model_data 以外の predicate（bow の pulling 等）は range_dispatch 単体で
                # 表現できないので記録して飛ばす。本パックには無い想定。
                skipped.append(pred)
        if skipped:
            skipped_pred.append((base, skipped))
        if not entries:
            continue

        entries.sort(key=lambda e: e["threshold"])
        item_def = {
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:custom_model_data",
                # fallback = ベースアイテムの素の見た目（CMD 未指定のとき）
                "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{base}"},
                "entries": entries,
            }
        }

        if dry_run:
            log(f"[dry-run] items/{base}.json <- {len(entries)} entries (CMD "
                f"{entries[0]['threshold']}..{entries[-1]['threshold']})")
        else:
            os.makedirs(items_dir, exist_ok=True)
            with open(os.path.join(items_dir, f"{base}.json"), "w", encoding="utf-8") as f:
                json.dump(item_def, f, ensure_ascii=False, indent=2)
            # ベースモデルから死蔵 overrides を除去
            model.pop("overrides", None)
            with open(mpath, "w", encoding="utf-8") as f:
                json.dump(model, f, ensure_ascii=False, indent=2)
        converted.append((base, len(entries)))

    log("")
    log("=== 変換サマリ ===")
    for base, n in converted:
        log(f"  items/{base}.json : {n} entries")
    log(f"  合計 {len(converted)} ベースアイテム / {sum(n for _, n in converted)} CMD エントリ")
    if skipped_pred:
        log("  ⚠ custom_model_data 以外の predicate を含み一部スキップ:")
        for base, preds in skipped_pred:
            log(f"     {base}: {preds}")
    return converted


CUSTOM_TEX_PREFIX = "block/mitoujr/"  # 自作テクスチャの移動先（blocks atlas・vanilla名と非衝突）


def fix_legacy_pack_issues(root, dry_run):
    """1.17 用パックを 26.1.2 で描画させるための旧仕様修正（resource-pack notes の実機ログ由来）。

    A) `parent: block/cube_all`（または `block/cube`）を継承するのに `all` テクスチャ未定義のモデルは、
       cube_all が宣言する `down/up/.../particle -> #all` が未解決になり、26.1.2 の厳格ローダが
       "Unresolved texture references: #down-> #all" として magenta 化する（独自 elements が #all を
       使っていなくても弾く）。独自 elements を完全定義しているので親を `block/block`
       （テクスチャ変数を宣言しない display 専用の基底）へ付け替えれば未解決参照が消える。
       ※ `all` を定義して cube_all を正当に使うモデル（hole_cobblestone/hole_dirt）は対象外。
    B) **アトラス統一**: 26.1.2 は 1 つの cuboid item モデルが複数アトラスのテクスチャを混在
       できない（"Multiple atlases used in model, expected blocks.png but also got items.png" →
       bake 失敗 → そのモデルを含む range_dispatch ベース(wheat_seeds 等)ごと全滅）。家具は
       vanilla の `block/*`(wool/iron＝blocks atlas) と自作 `item/*`/`items/*`(items atlas) を
       混ぜるため死ぬ。→ **自作テクスチャを全て `textures/block/mitoujr/` へ移動**し（blocks atlas・
       directory source は再帰なので拾われる／サブディレクトリで vanilla 名と衝突しない）、
       モデルの `item/X`・`items/X` 参照のうち**パック同梱（=自作）テクスチャ**を `block/mitoujr/X` へ
       書き換える。vanilla item テクスチャ参照（item/wheat_seeds 等の fallback）は対象外。
    C) particle 欠落の補完: elements を持つのに `particle` 未定義のモデルに、使用中の face テクスチャを
       particle として補う（"Missing texture references: particle" 警告の解消・同一アトラス維持）。
    """
    tex_root = os.path.join(root, "assets", "minecraft", "textures")
    item_dir = os.path.join(tex_root, "item")
    items_dir = os.path.join(tex_root, "items")
    dst_dir = os.path.join(tex_root, "block", "mitoujr")
    models_item = os.path.join(root, "assets", "minecraft", "models", "item")

    # B-1) 自作テクスチャ（textures/item/* と textures/items/*）を block/mitoujr/ へ移動。
    #      移動した basename 集合 = 「自作」判定に使う（vanilla item 参照は書き換えない）。
    custom = {}  # basename(拡張子なし) -> 元の論理prefix集合 はここでは不要、存在判定に basename を使う
    moved = 0
    for srcdir in (item_dir, items_dir):
        if not os.path.isdir(srcdir):
            continue
        for fn in sorted(os.listdir(srcdir)):
            src = os.path.join(srcdir, fn)
            if os.path.isfile(src) and fn.endswith(".png"):
                if not dry_run:
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.move(src, os.path.join(dst_dir, fn))
                custom[fn[:-4]] = True
                moved += 1
            elif os.path.isdir(src):
                # サブディレクトリ（book_cover/ 等）も丸ごと移動
                for sub in sorted(os.listdir(src)):
                    if sub.endswith(".png"):
                        if not dry_run:
                            os.makedirs(os.path.join(dst_dir, fn), exist_ok=True)
                            shutil.move(os.path.join(src, sub), os.path.join(dst_dir, fn, sub))
                        custom[f"{fn}/{sub[:-4]}"] = True
                        moved += 1
        if not dry_run and os.path.isdir(srcdir) and not os.listdir(srcdir):
            os.rmdir(srcdir)

    def rewrite_ref(v):
        """texture 値が自作テクスチャ参照なら block/mitoujr/ へ。それ以外（vanilla）は据置。"""
        if not isinstance(v, str):
            return v
        for pre in ("minecraft:items/", "items/", "minecraft:item/", "item/"):
            if v.startswith(pre):
                name = v[len(pre):]
                if name in custom:
                    return CUSTOM_TEX_PREFIX + name
        return v

    # A+B-2+C) 全モデル走査
    parent_rewrites, ref_rewrites, particle_added = [], 0, 0
    CUBE_PARENTS = {"minecraft:block/cube_all", "block/cube_all",
                    "minecraft:block/cube", "block/cube"}
    for fn in sorted(os.listdir(models_item)) if os.path.isdir(models_item) else []:
        if not fn.endswith(".json"):
            continue
        mpath = os.path.join(models_item, fn)
        try:
            with open(mpath, encoding="utf-8") as f:
                model = json.load(f)
        except json.JSONDecodeError:
            continue
        changed = False
        tex = model.setdefault("textures", {}) if "textures" in model else model.get("textures", {})
        # B-2) 自作テクスチャ参照の書き換え
        for k, v in list(tex.items()):
            nv = rewrite_ref(v)
            if nv != v:
                tex[k] = nv
                ref_rewrites += 1
                changed = True
        # A) cube_all 親の付け替え
        if model.get("parent") in CUBE_PARENTS and "all" not in tex:
            model["parent"] = "minecraft:block/block"
            parent_rewrites.append(fn[:-5])
            changed = True
        # C) particle 補完（elements を持ち particle 未定義のとき、使用 face テクスチャを流用）
        if model.get("elements") and tex and "particle" not in tex:
            used = [f.get("texture") for el in model["elements"]
                    for f in el.get("faces", {}).values() if f.get("texture", "").startswith("#")]
            for u in used:
                key = u[1:]
                if key in tex and isinstance(tex[key], str):
                    tex["particle"] = tex[key]
                    particle_added += 1
                    changed = True
                    break
        if changed:
            if tex and "textures" not in model:
                model["textures"] = tex
            if not dry_run:
                with open(mpath, "w", encoding="utf-8") as f:
                    json.dump(model, f, ensure_ascii=False, indent=2)

    log("")
    log("=== 旧仕様修正 ===")
    log(f"  A) cube_all親→block/block: {len(parent_rewrites)} モデル")
    log(f"  B) 自作テクスチャ→{CUSTOM_TEX_PREFIX}: {moved} ファイル移動 / 参照書換 {ref_rewrites} 箇所")
    log(f"  C) particle 補完: {particle_added} モデル")


def rezip(root, out_path):
    """ルートに assets/ が来る形で zip（cd root && zip -r ../out .）。"""
    out_abs = os.path.abspath(out_path)
    if os.path.exists(out_abs):
        os.remove(out_abs)
    # zip コマンドで store/deflate を素直に。CWD を root にして相対 'assets/...' を保つ
    subprocess.run(["zip", "-r", "-q", out_abs, "."], cwd=root, check=True)
    sha1 = hashlib.sha1(open(out_abs, "rb").read()).hexdigest()
    size = os.path.getsize(out_abs)
    log("")
    log(f"=== 出力 ===")
    log(f"  {out_abs}")
    log(f"  size: {size} bytes")
    log(f"  sha1: {sha1}")
    log(f"  → server.properties の resource-pack-sha1 をこの値に更新し、サーバ再起動")
    print(sha1)  # stdout には sha1 だけ


def main():
    ap = argparse.ArgumentParser(description="旧CMDリソパ→1.21.4+ item definition 移行")
    ap.add_argument("--in", dest="src", required=True, help="入力 zip またはディレクトリ")
    ap.add_argument("--out", dest="out", help="出力 zip（--dry-run 時は不要）")
    ap.add_argument("--pack-format", type=int, default=46,
                    help="新 pack_format（1.21.4=46 等。本番版に合わせる。既定46）")
    ap.add_argument("--dry-run", action="store_true", help="書き込まず変換内容だけ表示")
    args = ap.parse_args()

    if not args.dry_run and not args.out:
        ap.error("--out は --dry-run でない時は必須")

    work = tempfile.mkdtemp(prefix="rpmigrate-")
    try:
        extract_source(args.src, work)
        root = find_assets_root(work)
        if not args.dry_run:
            update_pack_mcmeta(root, args.pack_format)
        else:
            log(f"[dry-run] pack_format -> {args.pack_format}")
        convert_overrides(root, args.dry_run)
        fix_legacy_pack_issues(root, args.dry_run)
        if not args.dry_run:
            rezip(root, args.out)
        else:
            log("\n[dry-run] 出力なし。--out 指定で実書き込み")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

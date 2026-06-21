#!/usr/bin/env python3
"""validate_pack.py — リソースパックの item モデルをオフラインで検証する。

クライアントを起動せずに、各 item モデルを parent 連鎖で flatten し
（パック内モデル + バニラ client jar のモデルを解決）、
  1) elements の各 face が参照する texture 変数が具体パスまで解決するか（未解決 #ref 検出）
  2) 解決先の texture ファイルがパック or バニラに実在するか（Missing texture 検出）
を確認する。26.1.2 クライアントが latest.log に吐く
"Unresolved texture references" / "Missing textures" を事前に再現するための lint。

使い方:
  python3 validate_pack.py <pack.zip> [<vanilla-client.jar>]
  （client jar 省略時は ~/Library/Application Support/minecraft/versions/26.1.2/26.1.2.jar）

終了コード: 問題ゼロで 0、検出ありで 1。
"""
import json
import os
import sys
import zipfile


def strip_ns(ref):
    return ref.split(":", 1)[1] if ":" in ref else ref


class Source:
    """パック zip とバニラ jar から model/texture を引く統合ソース（パック優先）。"""
    def __init__(self, pack_zip, vanilla_jar):
        self.z = [zipfile.ZipFile(pack_zip)]
        if vanilla_jar and os.path.exists(vanilla_jar):
            self.z.append(zipfile.ZipFile(vanilla_jar))
        self._names = [set(z.namelist()) for z in self.z]

    def read_model(self, ref):
        path = f"assets/minecraft/models/{strip_ns(ref)}.json"
        for z, names in zip(self.z, self._names):
            if path in names:
                return json.loads(z.read(path))
        return None

    def texture_exists(self, ref):
        path = f"assets/minecraft/textures/{strip_ns(ref)}.png"
        return any(path in names for names in self._names)


def flatten(source, ref, _seen=None):
    """parent 連鎖を辿り (textures_map, elements, found_chain) を返す。子が親を上書き。"""
    _seen = _seen or set()
    if ref in _seen:
        return {}, [], []
    _seen.add(ref)
    if strip_ns(ref).startswith("builtin/"):
        return {}, [], [(ref, True)]  # builtin/generated 等は組込みで実体不要
    model = source.read_model(ref)
    if model is None:
        return {}, [], [(ref, False)]
    textures, elements, chain = {}, None, [(ref, True)]
    if "parent" in model:
        ptex, pelem, pchain = flatten(source, model["parent"], _seen)
        textures.update(ptex)
        elements = pelem
        chain = pchain + chain
    textures.update(model.get("textures", {}))
    if "elements" in model:
        elements = model["elements"]
    return textures, (elements or []), chain


def resolve_var(textures, key, _depth=0):
    """'#all' のような変数を具体パスまで解決。未解決なら None。"""
    if _depth > 16:
        return None
    if not key.startswith("#"):
        return key  # 既に具体パス
    val = textures.get(key[1:])
    if val is None:
        return None
    return resolve_var(textures, val, _depth + 1) if val.startswith("#") else val


def is_atlas_dir(path):
    """26.1.2 のアトラスが stitch する texture ディレクトリか（block/ と item/ のみ）。"""
    p = strip_ns(path)
    return p.startswith("block/") or p.startswith("item/")


def atlas_of(path):
    """texture パスが属するアトラス名（block/→blocks, item/→items）。"""
    p = strip_ns(path)
    return "blocks" if p.startswith("block/") else "items" if p.startswith("item/") else "?"


def validate_model(source, ref):
    """1 モデルを検証し問題リストを返す。"""
    problems = []
    textures, elements, chain = flatten(source, ref)
    missing_parent = [c for c, ok in chain if not ok]
    if missing_parent:
        problems.append(f"missing parent/model: {missing_parent}")

    # (1) elements の各 face が参照する texture（実描画される）の解決と実在
    used_keys = set()
    for el in elements:
        for face in el.get("faces", {}).values():
            t = face.get("texture")
            # '#missing' は Blockbench が未割当面に振る sentinel（内部に隠れる面）。
            # バニラも警告せず実害なしのため検査対象外。
            if t and t != "#missing":
                used_keys.add(t)
    atlases = set()
    for key in sorted(used_keys):
        concrete = resolve_var(textures, key)
        if concrete is None:
            problems.append(f"unresolved used texture ref {key} (-> {textures.get(key[1:], '?')})")
        elif not source.texture_exists(concrete):
            problems.append(f"missing texture file: {concrete}")
        elif not is_atlas_dir(concrete):
            problems.append(f"texture not in atlas dir (block/ or item/): {concrete}")
        else:
            atlases.add(atlas_of(concrete))
    # cuboid item モデルは単一アトラスしか使えない（26.1.2: "Multiple atlases used in model"
    # → bake 失敗 → そのモデルを含む range_dispatch ベースごと全滅）。
    if len(atlases) > 1:
        problems.append(f"MIXED ATLASES (bake失敗): {sorted(atlases)} を1モデルで混在")

    # (2) flatten 後に「宣言された」texture 変数が未解決でないか
    #     （クライアントの "Unresolved texture references" 警告＝cube_all の #all 等を再現）
    for k, v in sorted(textures.items()):
        if isinstance(v, str) and v.startswith("#") and resolve_var(textures, v) is None:
            problems.append(f"declared var '{k}' -> {v} unresolved")
    return problems


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    pack = sys.argv[1]
    vanilla = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
        "~/Library/Application Support/minecraft/versions/26.1.2/26.1.2.jar")
    source = Source(pack, vanilla)
    z = zipfile.ZipFile(pack)

    # 実際に描画されるモデル集合 = items/ 定義(range_dispatch 等)が参照するモデル
    # ＋ バニラ item と同名で直接置換する item モデル（generated 系のテクスチャ差し替え）。
    # base モデル（item/mid 等・どの items/ からも参照されない）は親としてのみ使われ
    # 単体描画されないので検査対象外（偽陽性を出さない）。
    rendered = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "minecraft:model" and isinstance(o.get("model"), str):
                rendered.add(strip_ns(o["model"]))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for n in z.namelist():
        if n.startswith("assets/minecraft/items/") and n.endswith(".json"):
            walk(json.loads(z.read(n)))
            rendered.add("item/" + os.path.basename(n)[:-5])  # 定義自身＝バニラ item の置換

    total_bad = 0
    for ref in sorted(rendered):
        if not ref.startswith("item/"):
            continue
        problems = validate_model(source, ref)
        if problems:
            total_bad += 1
            print(f"✗ {ref}")
            for p in problems:
                print(f"    {p}")
    n_checked = len([r for r in rendered if r.startswith("item/")])
    print(f"\n=== 描画モデル {n_checked} 件中 {total_bad} 件に問題 "
          f"{'(クリーン)' if total_bad == 0 else ''} ===")
    sys.exit(1 if total_bad else 0)


if __name__ == "__main__":
    main()

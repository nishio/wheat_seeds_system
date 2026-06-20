# modernize — convert classic Wheat Seeds packs to Minecraft 1.21.4+

The classic generator emits the pre-1.21.4 resource-pack layout:

- `pack.mcmeta` with `pack_format: 7` (MC 1.17 era)
- base items (`wheat_seeds`, …) carry `overrides` + `custom_model_data` *predicates*
  in `assets/minecraft/models/item/<base>.json`

Minecraft 1.21.4 (and the 26.x calendar versions) removed that format. Custom items
silently fall back to the plain base item. These two scripts convert a built pack to
the new format and verify it offline — no client launch required.

## `migrate.py`

Converts a built pack (zip **or** directory) to the 1.21.4+ item-model format.

```
python3 migrate.py --in <pack.zip|dir> --out <out.zip> --pack-format <N>
python3 migrate.py --in <pack.zip>      --dry-run        # show changes only
```

What it does:

1. `pack.mcmeta` → new `pack_format`, plus `min_format`/`max_format` (mandatory once
   `pack_format > 64`; otherwise the client rejects the metadata).
2. For each base item that has `overrides`, emits `assets/minecraft/items/<base>.json`
   with a `range_dispatch` on `minecraft:custom_model_data` (each old CMD → a threshold
   entry, `fallback` = the plain base model) and strips the dead `overrides`.
3. Fixes three issues that otherwise break baking on 1.21.4:
   - **mixed atlases** — a single cuboid model that pulls from both `block/` and `item/`
     fails to bake (and takes its whole `range_dispatch` base down with it). Custom item
     textures are consolidated under `textures/block/mitoujr/` (sub-dir avoids vanilla
     name clashes) so every cuboid stays in one atlas.
   - **`cube_all` `#all`** — models inheriting `block/cube_all` without an `all` texture
     leave `#all` unresolved → magenta. Re-parented to `block/block`.
   - missing **`particle`** texture key — filled in.

Existing placed items (e.g. a `wheat_seeds` with integer `custom_model_data=100` inside
a frame) keep working: the world's DataFixerUpper rewrites the old integer CMD to the
component's `floats[0]`, which matches the `range_dispatch` thresholds — so swapping the
pack is enough, no re-placing.

## `validate_pack.py`

Offline lint. Flattens every rendered model through its parent chain (resolving against
the pack **and** a vanilla client jar) and reports unresolved `#refs`, missing texture
files, textures outside an atlas dir, and **mixed-atlas** models.

```
python3 validate_pack.py <pack.zip> [<vanilla-client.jar>]
# default jar: ~/Library/Application Support/minecraft/versions/26.1.2/26.1.2.jar
```

Exit code 0 = clean, 1 = problems found. Run it before deploying a pack.

# Wheat Seeds System — User Guide

**Canonical guide.** This file is the up-to-date documentation; the Planet Minecraft
blog, the pack pages, and the (Japanese) Scrapbox page link here.

**Wheat Seeds System** places custom 3D models in a vanilla Minecraft world **without any
client-side mod** — it uses only the resource pack + the vanilla custom-model mechanism.
Each piece of furniture is a base item (wheat seeds, etc.) carrying a custom model, held
inside an **invisible item frame**, placed on an **invisible barrier** block.

It was created for the **Cybozu Hackathon 2021** (to build a virtual office that employees
and their families could visit) and has been used for furniture, gardens, books, lights and more.

## How it works (3 parts)

1. **Base item = the "carrier" for the model.** Items you rarely hold — `wheat_seeds`
   (and `wooden_pickaxe` / `stick`) — carry the model, switched by `custom_model_data`.
   Borrowing a rarely-used item means the swap does no harm to normal gameplay.
2. **Invisible item frame = where the model is displayed.** Because you can rotate the
   frame, a model can face 45°-step directions, and can even look like it breaks the
   one-axis cuboid rotation limit.
3. **Invisible barrier = the floor / hitbox.** Chairs sit on a barrier so you can
   stand/sit on them (sitting needs a "sit on block" plugin such as GSit). For a desk,
   use the desk block as the base instead of a barrier.

## Commands (Minecraft 1.21.4+)

> Minecraft **1.20.5** replaced item NBT (`{...}`) with **components** (`[...]`), and
> **1.21.4** moved custom item models to *item definitions* (`range_dispatch`). Use the
> syntax below on modern versions.

Give a custom item (replace `<ID>` with a number from the [ID list](#id-list-custom_model_data)):

```mcfunction
/minecraft:give @s wheat_seeds[minecraft:custom_model_data={floats:[<ID>]}]
```

Use `/minecraft:give` — plain `/give` is taken over by EssentialsX and fails with
`unknown item name`. (If the ID doesn't exist, you get a plain wheat-seeds item with no model.)

Invisible item frame:

```mcfunction
/minecraft:give @s item_frame[entity_data={id:"minecraft:item_frame",Invisible:true}]
```

Make the **nearest placed** frame invisible / fixed (entity NBT via `/data` is unchanged):

```mcfunction
/data modify entity @e[type=minecraft:item_frame,nbt={Invisible:0b},limit=1,sort=nearest] Invisible set value 1b
/data modify entity @e[type=minecraft:item_frame,nbt={Fixed:0b},limit=1,sort=nearest] Fixed set value 1b
```

<details><summary>Legacy syntax (Minecraft 1.17 – 1.20.4)</summary>

```mcfunction
/give @p wheat_seeds{CustomModelData:<ID>}
/give @p item_frame{EntityTag:{Invisible:1b}}
```
</details>

## Modeling notes (for creators)

- Effective size up to **6×6×6** (vanilla shrinks an item-frame model ×0.5, so models are
  authored at ×4 scale).
- A model whose item frame leaves your view **disappears** (entity cull) — large models
  only work where players don't get close.
- On 1.21.4+, a single cuboid model must use **one texture atlas**: mixing `block/` and
  `item/` textures in one model fails to bake. Keep a model's textures in one atlas
  (e.g. put custom textures under `textures/block/...`).

## Packs

All packs use the Wheat Seeds System. For **Minecraft 1.21.4+** download the file named
`*-mc1214.zip`; the older files remain for earlier versions.

| Pack | Planet Minecraft |
|---|---|
| Colorful Chairs | https://www.planetminecraft.com/texture-pack/colorful-chairs |
| Cactus Arm and Flowers | https://www.planetminecraft.com/texture-pack/cactus-arm-and-flowers/ |
| Laptop, Desktop and Keyboards | https://www.planetminecraft.com/texture-pack/laptop-desktop-and-keyboards/ |
| Umbrella | https://www.planetminecraft.com/texture-pack/umbrella-5379102/ |
| Diagonal Blocks | https://www.planetminecraft.com/texture-pack/diagonal-blocks-5379207/ |
| Decoration Lights | https://www.planetminecraft.com/texture-pack/decoration-lights/ |
| Books | https://www.planetminecraft.com/texture-pack/books-5387457/ |
| Desks | https://www.planetminecraft.com/texture-pack/desks/ |
| KareSanSui Japanese Traditional Sand Garden | https://www.planetminecraft.com/texture-pack/karesansui-japanese-traditional-sand-garden/ |
| Invisible Holes | https://www.planetminecraft.com/texture-pack/invisible-holes/ |

## ID list (custom_model_data)

Color series follow this order (`+1` each): `white, orange, magenta, light_blue, yellow,
lime, pink, gray, light_gray, cyan, purple, blue, brown, green, red, black`.

| Range | Pack | Items |
|---|---|---|
| 100–195 | Colorful Chairs | 100 round_chair, 120 chair, 140 tall_chair, 160 chair_with_desk, 180 chair_with_arm (each `+ color`; e.g. 100 = round_chair_white … 115 = round_chair_black) |
| 500–502 | Cactus | 500 cactus_arm, 501 cactus_flower, 502 cactus_flower2 |
| 600–604 | Laptop, Desktop and Keyboard | 600 macbook, 601 desktop, 602 monitor, 603 keyboard, 604 ipad |
| 700–721 | Umbrella | 700 umbrella_up_white, 701 umbrella_up_red, 720 umbrella_down_white, 721 umbrella_down_red |
| 800–895 | Diagonal Blocks | diagonal1…5 at 800 / 820 / 840 / 860 / 880 (each `+ color`) |
| 900–914 | Decoration Lights | 900–908 decolight1–9, 910–913 ceil_light1–4, 914 ceil_light_cloud |
| 1000–1002 | Desks | 1000 glass_table_1x1, 1001 glass_table_3x2, 1002 pc_table_4x2 |
| 1100–1119 | Books | 1100–1109 simple_book_0–9, 1110–1119 book_0–9 |
| 1200–1206 | KareSanSui | 1200 kss_1x1_straight, 1201 kss_1x1_curve, 1202 kss_2x2_straight, 1203 kss_2x2_curve, 1204 kss_2x2_circle, 1205 kss_3x3_straight, 1206 kss_3x3_circle |
| 1300–1301 | Invisible Holes | 1300 hole_dirt, 1301 hole_cobblestone |

The authoritative, always-current list is generated to [`toc.md`](toc.md) by the build.

## For pack builders

The generator (`generator.py`) builds the packs; `build_mitoujr.sh` and the
[`modernize/`](modernize/README.md) step convert them to the 1.21.4+ item-model format
and validate them offline. See [`modernize/README.md`](modernize/README.md).

## Links

- Generator (source): https://github.com/nishio/wheat_seeds_system
- Slide (Cybozu Hackathon 2021): https://docs.google.com/presentation/d/1MQUx9hC2MEXWYCoXcmlLVHFBsV6k9_A8fzVUNfggHr8/edit
- Japanese guide (Scrapbox): https://scrapbox.io/nishio/WheatSeedsSystem

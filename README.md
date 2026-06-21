# Wheat Seeds System

Wheat Seeds System is a system for placing custom models in the Minecraft world.
It was developed to build a virtual office for Cybozu/Kintone branches around the world for the Cybozu Hackathon in 2021. ([Slide for Cybozu Hackathon 2021](https://docs.google.com/presentation/d/1MQUx9hC2MEXWYCoXcmlLVHFBsV6k9_A8fzVUNfggHr8/edit?usp=sharing))

With this system, custom models do not harm existing models.
Also, this system does not require any client-side MOD. The main technologies are the resource pack mechanism and the custom model override mechanism supported by the vanilla client.

[User Guide](https://scrapbox.io/nishio/WheatSeedsSystem)

## Minecraft 1.21.4+ (item components & model overhaul)

Minecraft changed how custom item models work, which breaks the classic packs:

- **1.20.5** replaced item NBT (`{...}`) with **data components** (`[...]`).
- **1.21.4** removed the `overrides` + `custom_model_data` *predicate* model format
  in favor of **item definitions** (`assets/minecraft/items/<item>.json`,
  `range_dispatch`). Classic packs render every custom item as the plain base item.

The classic generator (`generator.py`) still emits the pre-1.21.4 layout. To get a
pack that works on 1.21.4+ run the **modernize** step — `build_mitoujr.sh` does this
automatically. To re-publish an individual pack, convert it:

```
python3 modernize/migrate.py --in chairs.zip --out chairs-1214.zip --pack-format 84
python3 modernize/validate_pack.py chairs-1214.zip   # offline check vs a vanilla client jar
```

`--pack-format` is the resource-pack format of your target version (e.g. `46` = 1.21.4,
`84` = MC 26.1.2). See [`modernize/README.md`](modernize/README.md) for details.

### Commands (1.21.4+)

Give a custom item (e.g. CustomModelData `600` = macbook; the integer goes into the
`custom_model_data` component's `floats` list, which `range_dispatch` reads at index 0):

```
/minecraft:give @s wheat_seeds[minecraft:custom_model_data={floats:[600]}]
```

Invisible item frame (entity data is now a component; `id` is required, booleans are `true`):

```
/minecraft:give @s item_frame[entity_data={id:"minecraft:item_frame",Invisible:true}]
```

Make the nearest **placed** frame invisible / fixed (entity NBT via `/data` is unchanged):

```
/data modify entity @e[type=minecraft:item_frame,nbt={Invisible:0b},limit=1,sort=nearest] Invisible set value 1b
/data modify entity @e[type=minecraft:item_frame,nbt={Fixed:0b},limit=1,sort=nearest] Fixed set value 1b
```

> `/give` (without the `minecraft:` namespace) is intercepted by EssentialsX and fails
> with `unknown item name`; use `/minecraft:give`.

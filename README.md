# Wheat Seeds System

Wheat Seeds System is a system for placing custom models in the Minecraft world.
It was developed to build a virtual office for Cybozu/Kintone branches around the world for the Cybozu Hackathon in 2021. ([Slide for Cybozu Hackathon 2021](https://docs.google.com/presentation/d/1MQUx9hC2MEXWYCoXcmlLVHFBsV6k9_A8fzVUNfggHr8/edit?usp=sharing))

With this system, custom models do not harm existing models.
Also, this system does not require any client-side MOD. The main technologies are the resource pack mechanism and the custom model override mechanism supported by the vanilla client.

## 📖 Documentation

- **[GUIDE.md](GUIDE.md)** — the canonical user guide (how it works, commands for
  Minecraft 1.21.4+, the full custom-model-data ID list, and all the packs). **Start here.**
- [`toc.md`](toc.md) — auto-generated ID index.
- [`modernize/README.md`](modernize/README.md) — converting/validating packs for 1.21.4+ (for builders).
- Japanese guide: [scrapbox.io/nishio/WheatSeedsSystem](https://scrapbox.io/nishio/WheatSeedsSystem)

## Quick start

Give a custom item (e.g. `600` = macbook; see [GUIDE.md](GUIDE.md#id-list-custom_model_data) for all IDs):

```mcfunction
/minecraft:give @s wheat_seeds[minecraft:custom_model_data={floats:[600]}]
```

> On Minecraft **1.21.4+** items use the component syntax above (item NBT `{...}` was
> removed in 1.20.5). Use `/minecraft:give` — plain `/give` is taken over by EssentialsX.
> Full details and the pre-1.21.4 legacy syntax are in [GUIDE.md](GUIDE.md).

## Building / modernizing

`generator.py` builds the classic packs; `build_mitoujr.sh` plus the
[`modernize/`](modernize/README.md) step convert them to the 1.21.4+ item-model format
(`assets/minecraft/items/<item>.json`, `range_dispatch`) and validate them offline against
a vanilla client jar. See [`modernize/README.md`](modernize/README.md).

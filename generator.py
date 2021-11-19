import cactus
import os
import json
import subprocess
import shutil
import pack


COLORS = "white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black".split()
assert len(COLORS) == 16
# 0:white 1:orange 2:magenta 3:light_blue 4:yellow 5:lime 6:pink 7:gray 8:light_gray
# 9:cyan 10:purple 11:blue 12:brown 13:green 14:red 15:black


def wool(color):
    return f"block/{color}_wool"


WOOL_TEXTURES = {c: wool(c) for c in COLORS}


def make_variation_reference(offset, prefix, texture_map, models):
    for id, k in enumerate(texture_map):
        name = f"{prefix}_{k}"
        assert offset + id not in models
        models[offset + id] = name


# model refernce definitions


def laptop_model_refs(models={}):
    models[600] = "macbook"
    models[601] = "desktop"
    models[602] = "monitor"
    # models[603] = "large_monitor"
    # models[604] = "wall_monitor"
    models[603] = "keyboard"
    models[604] = "ipad"
    return models


def chair_model_refs(models={}):
    sections = [
        (100, "round_chair"),
        (120, "chair"),
        (140, "tall_chair"),
        (160, "chair_with_desk"),
        (180, "chair_with_arm"),
    ]
    for offset, name in sections:
        make_variation_reference(offset, name, WOOL_TEXTURES, models)
    return models


UMBRELLA_TEXTURES = {"white": "white_triangle",
                     "red": "red_triangle"}


def umbrella_model_refs(models={}):
    make_variation_reference(700, "umbrella_up", UMBRELLA_TEXTURES, models)
    make_variation_reference(720, "umbrella_down", UMBRELLA_TEXTURES, models)
    return models


def add_model_refs(offset, refs, models):
    for i, ref in enumerate(refs):
        id = offset + i
        assert id not in models
        models[id] = ref
    return models


def diagonal_model_refs(models={}):
    return add_model_refs(
        800,
        ["diagonal1", "diagonal2",
         "diagonal3", "diagonal4", "diagonal5"], models)


def all_model_refs():
    models = {}
    models = cactus.model_refs(models)
    models = laptop_model_refs(models)
    models = chair_model_refs(models)
    models = umbrella_model_refs(models)
    models = diagonal_model_refs(models)
    return models


LAPTOP_TEXTURES = [
    "black", "desktop", "keyboard",
    "macbook", "monitor_arm", "monitor_frame", "white"]


def build_laptop_pack(all_models):
    PACK_NAME = "laptop"
    PACK_DESC = "Laptop, Desktop and Keyboard"
    pack.ready(all_models)
    models = laptop_model_refs({})
    pack.copy_files("common", models.values(), LAPTOP_TEXTURES)

    pack.finish(PACK_NAME, PACK_DESC)


def build_chair_pack(all_models):
    PACK_NAME = "chairs"
    PACK_DESC = "Colorful Chairs"
    pack.ready(all_models)
    models = chair_model_refs({})
    BASES = ["round_chair", "chair", "tall_chair",
             "chair_with_desk", "chair_with_arm"]

    for base in BASES:
        pack.make_variation_modelfiles(
            base,
            f"item/{base}",
            "seat", WOOL_TEXTURES
        )

    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", BASES, ["black", "mesh"])

    pack.finish(PACK_NAME, PACK_DESC)


def build_umbrella(all_models):
    PACK_NAME = "umbrella"
    PACK_DESC = "Umbrella"
    pack.ready(all_models)
    models = umbrella_model_refs({})
    pack.make_variation_modelfiles(
        "umbrella_up",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.make_variation_modelfiles(
        "umbrella_down",
        "item/umbrella_down",
        "0", UMBRELLA_TEXTURES
    )
    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", ["umbrella_up", "umbrella_down"],
                    UMBRELLA_TEXTURES.values())

    pack.finish(PACK_NAME, PACK_DESC)


def build_diagonal(all_models):
    # it is experimental pack, so it is not included in all-in-one pack
    PACK_NAME = "diagonal"
    PACK_DESC = "Diagonal Blocks"
    pack.ready(all_models)
    models = diagonal_model_refs({})
    pack.copy_files("common", models.values(), [])

    pack.finish(PACK_NAME, PACK_DESC)


def build_all_in_one_pack(all_models):
    PACK_NAME = "all-in-one"
    PACK_DESC = "All-in-one Wheat Seeds System"
    pack.ready(all_models)
    # cactus
    models = cactus.model_refs({})
    pack.copy_files("common", models.values(), cactus.TEXTURES)

    # laptop
    models = laptop_model_refs({})
    pack.copy_files("common", models.values(), LAPTOP_TEXTURES)
    # chairs
    models = chair_model_refs({})
    BASES = ["round_chair", "chair", "tall_chair",
             "chair_with_desk", "chair_with_arm"]

    for base in BASES:
        pack.make_variation_modelfiles(
            base,
            f"item/{base}",
            "seat", WOOL_TEXTURES
        )

    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", BASES, ["black", "mesh"])
    # umbrella
    models = umbrella_model_refs({})
    pack.make_variation_modelfiles(
        "umbrella_up",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.make_variation_modelfiles(
        "umbrella_down",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", ["umbrella_up", "umbrella_down"],
                    UMBRELLA_TEXTURES.values())
    # end
    pack.finish(PACK_NAME, PACK_DESC)


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)


def main():
    all_models = all_model_refs()
    cactus.build(all_models)
    build_laptop_pack(all_models)
    build_chair_pack(all_models)
    build_umbrella(all_models)
    build_diagonal(all_models)
    build_all_in_one_pack(all_models)


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

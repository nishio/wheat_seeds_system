import os
import json
import subprocess
import shutil

TARGET_DIR = "generated"
ITEM_DIR = f"{TARGET_DIR}/assets/minecraft/models/item"


COLORS = "white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black".split()
assert len(COLORS) == 16
# 0:white 1:orange 2:magenta 3:light_blue 4:yellow 5:lime 6:pink 7:gray 8:light_gray
# 9:cyan 10:purple 11:blue 12:brown 13:green 14:red 15:black


def wool(color):
    return f"block/{color}_wool"


WOOL_TEXTURES = {c: wool(c) for c in COLORS}


def _make_color_variation(offset, prefix, parent, texture_name, color_type, models):
    for id, color in enumerate(COLORS):
        data = {
            "parent": parent,
            "textures": {texture_name: color_type(color)}
        }
        name = f"{prefix}_{color}"
        # write_item(data, name)
        assert offset + id not in models
        models[offset + id] = name


def make_variation(offset, prefix, parent, texture_name, texture_map, models):
    """
    >>> models = {}
    >>> make_variation(0, "chair", "item/chair", "seat", WOOL_TEXTURES, models)
    >>> models2 = {}
    >>> _make_color_variation(0, "chair", "item/chair", "seat", wool, models2)
    >>> models == models2
    True
    """
    for id, (k, v) in enumerate(texture_map.items()):
        data = {
            "parent": parent,
            "textures": {texture_name: v}
        }
        name = f"{prefix}_{k}"
        write_item(data, name)
        assert offset + id not in models
        models[offset + id] = name


def write_item(data, name):
    path = os.path.join(
        ITEM_DIR, f"{name}.json")
    json.dump(data, open(path, "w"), indent=2)
    print(f"wrote {name}, {path}")


def cactus_models(models={}):
    models[500] = "cactus_arm"
    models[501] = "cactus_flower"
    models[502] = "cactus_flower2"
    return models


def laptop_models(models={}):
    models[600] = "macbook"
    models[601] = "desktop"
    models[602] = "monitor"
    # models[603] = "large_monitor"
    # models[604] = "wall_monitor"
    models[603] = "keyboard"
    models[604] = "ipad"
    return models


def chair_models(models={}):
    # 100-115
    make_variation(
        100, "round_chair",
        "item/round_chair",
        "seat", WOOL_TEXTURES, models
    )

    # 120-135
    make_variation(
        120, "chair",
        "item/chair",
        "seat", WOOL_TEXTURES, models
    )

    # 140-155
    make_variation(
        140, "tall_chair",
        "item/tall_chair",
        "seat", WOOL_TEXTURES, models
    )

    # 160-175
    make_variation(
        160, "chair_with_desk",
        "item/chair_with_desk",
        "seat", WOOL_TEXTURES, models
    )

    # 180-195
    make_variation(
        180, "chair_with_arm",
        "item/chair_with_arm",
        "seat", WOOL_TEXTURES, models
    )

    return models


def generate_wheat_seeds(models):
    # put models into wheat_seeds
    SEED = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "minecraft:item/wheat_seeds",
            "particle": "minecraft:item/wheat_seeds"
        },
        "overrides": []
    }

    overrides = SEED["overrides"]

    for id in models:
        name = models[id]
        model = name
        if "item/" not in model:
            model = f"item/{model}"

        x = {
            "predicate": {"custom_model_data": id},
            "model": model
        }
        print(id, name)
        overrides.append(x)

    write_item(SEED, "wheat_seeds")


def copy_files(frm, items, textures=[], to="build"):
    ITEMS_DST = f"{to}/assets/minecraft/models/item"
    ITEMS_SRC = f"{frm}/assets/minecraft/models/item"
    os.makedirs(ITEMS_DST, exist_ok=True)
    print(f"copy items into {ITEMS_DST}")
    for item in items:
        print("copy", item)
        shutil.copy(f"{ITEMS_SRC}/{item}.json", ITEMS_DST)

    TEXTURES_DST = f"{to}/assets/minecraft/textures/item"
    TEXTURES_SRC = f"{frm}/assets/minecraft/textures/item"
    os.makedirs(TEXTURES_DST, exist_ok=True)
    print(f"copy textures into {TEXTURES_DST}")
    for texture in textures:
        print("copy", texture)
        shutil.copy(f"{TEXTURES_SRC}/{texture}.png", TEXTURES_DST)


def write_mcmeta(desc, dst="build"):
    mcmeta = {
        "pack": {
            "pack_format": 7,
            "description": desc
        }
    }
    json.dump(mcmeta, open(f"{dst}/pack.mcmeta", "w"), indent=2)


def zip(name):
    target = os.path.abspath(f"{name}.zip")
    if os.path.isfile(target):
        os.remove(target)
    os.chdir(name)
    subprocess.check_call(["zip", "-r", target, "."])
    os.chdir("..")


def build_cactus_pack():
    PACK_NAME = "cactus"
    PACK_DESC = "Cactus Arm and Flowers"
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)
    models = cactus_models()

    shutil.rmtree("build", ignore_errors=True)
    generate_wheat_seeds(models)
    copy_files("generated", ["wheat_seeds"])

    copy_files(
        "common",
        models.values(),
        ["cactus_flower", "cactus_flower2"])

    # make `pack.mcmeta`
    write_mcmeta(PACK_DESC)

    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    zip(PACK_NAME)


def build_laptop_pack():
    PACK_NAME = "laptop"
    PACK_DESC = "Laptop, Desktop and Keyboard"
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)
    models = laptop_models()

    shutil.rmtree("build", ignore_errors=True)
    generate_wheat_seeds(models)
    copy_files("generated", ["wheat_seeds"])

    copy_files(
        "common",
        models.values(),
        ["black", "desktop", "keyboard", "macbook", "monitor_arm", "monitor_frame", "white"])

    # make `pack.mcmeta`
    write_mcmeta(PACK_DESC)

    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    zip(PACK_NAME)


def build_chair_pack():
    PACK_NAME = "chairs"
    PACK_DESC = "Colorful Chairs"
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)
    models = chair_models()

    shutil.rmtree("build", ignore_errors=True)
    generate_wheat_seeds(models)
    copy_files("generated", ["wheat_seeds"])

    copy_files(
        "generated",
        models.values(),
        [])
    copy_files(
        "common",
        ["round_chair", "chair", "tall_chair",
            "chair_with_desk", "chair_with_arm"],
        ["black", "mesh", "keyboard", "macbook", "monitor_arm", "monitor_frame", "white"])

    # make `pack.mcmeta`
    write_mcmeta(PACK_DESC)

    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    zip(PACK_NAME)


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)


def main():
    build_cactus_pack()
    build_laptop_pack()
    build_chair_pack()


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

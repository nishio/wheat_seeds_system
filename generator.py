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


def make_variation_reference(offset, prefix, texture_map, models):
    for id, k in enumerate(texture_map):
        name = f"{prefix}_{k}"
        assert offset + id not in models
        models[offset + id] = name


def make_variation_modelfiles(prefix, parent, texture_name, texture_map):
    for k, v in texture_map.items():
        data = {
            "parent": parent,
            "textures": {texture_name: v}
        }
        name = f"{prefix}_{k}"
        write_item(data, name)


def write_item(data, name):
    path = os.path.join(
        ITEM_DIR, f"{name}.json")
    json.dump(data, open(path, "w"), indent=2)
    print(f"wrote {name}, {path}")

# model refernce definitions


def cactus_model_refs(models={}):
    models[500] = "cactus_arm"
    models[501] = "cactus_flower"
    models[502] = "cactus_flower2"
    return models


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


def all_model_refs():
    models = {}
    models = cactus_model_refs(models)
    models = laptop_model_refs(models)
    models = chair_model_refs(models)
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


def ready_pack():
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)
    all_models = all_model_refs()

    shutil.rmtree("build", ignore_errors=True)
    generate_wheat_seeds(all_models)
    copy_files("generated", ["wheat_seeds"])


def finish_pack(PACK_NAME, PACK_DESC):
    # make `pack.mcmeta`
    write_mcmeta(PACK_DESC)
    # rename `build` to pack name and zip
    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    zip(PACK_NAME)


CACTUS_TEXTURES = ["cactus_flower", "cactus_flower2"]


def build_cactus_pack():
    PACK_NAME = "cactus"
    PACK_DESC = "Cactus Arm and Flowers"
    ready_pack()
    models = cactus_model_refs({})
    copy_files("common", models.values(), CACTUS_TEXTURES)
    finish_pack(PACK_NAME, PACK_DESC)


LAPTOP_TEXTURES = [
    "black", "desktop", "keyboard",
    "macbook", "monitor_arm", "monitor_frame", "white"]


def build_laptop_pack():
    PACK_NAME = "laptop"
    PACK_DESC = "Laptop, Desktop and Keyboard"
    ready_pack()
    models = laptop_model_refs({})
    copy_files("common", models.values(), LAPTOP_TEXTURES)

    finish_pack(PACK_NAME, PACK_DESC)


def build_chair_pack():
    PACK_NAME = "chairs"
    PACK_DESC = "Colorful Chairs"
    ready_pack()
    models = chair_model_refs({})
    BASES = ["round_chair", "chair", "tall_chair",
             "chair_with_desk", "chair_with_arm"]

    for base in BASES:
        make_variation_modelfiles(
            base,
            f"item/{base}",
            "seat", WOOL_TEXTURES
        )

    copy_files("generated", models.values(), [])
    copy_files("common", BASES, ["black", "mesh"])

    finish_pack(PACK_NAME, PACK_DESC)


def build_all_in_one_pack():
    PACK_NAME = "all-in-one"
    PACK_DESC = "All-in-one Wheat Seeds System"
    ready_pack()
    # cactus
    models = cactus_model_refs({})
    copy_files("common", models.values(), CACTUS_TEXTURES)

    # laptop
    models = laptop_model_refs({})
    copy_files("common", models.values(), LAPTOP_TEXTURES)
    # chairs
    models = chair_model_refs({})
    BASES = ["round_chair", "chair", "tall_chair",
             "chair_with_desk", "chair_with_arm"]

    for base in BASES:
        make_variation_modelfiles(
            base,
            f"item/{base}",
            "seat", WOOL_TEXTURES
        )

    copy_files("generated", models.values(), [])
    copy_files("common", BASES, ["black", "mesh"])
    # end
    finish_pack(PACK_NAME, PACK_DESC)


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
    build_all_in_one_pack()


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

import shutil
import os
import json
import subprocess

TARGET_DIR = "generated"
ITEM_DIR = f"{TARGET_DIR}/assets/minecraft/models/item"


def assure_item(name):
    if "item/" not in name:
        name = f"item/{name}"
    return name


def write_item(data, name):
    path = os.path.join(
        ITEM_DIR, f"{name}.json")
    json.dump(data, open(path, "w"), indent=2)
    # print(f"wrote {name}, {path}")


def make_variation_modelfiles(prefix, parent, texture_name, texture_map):
    for k, v in texture_map.items():
        data = {
            "parent": parent,
            "textures": {texture_name: assure_item(v)}
        }
        name = f"{prefix}_{k}"
        write_item(data, name)


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

    # sort required because of Minecraft behavoir
    # (if model with larger CustomModelData appears first, it will be ignored)
    for id in sorted(models):
        name = models[id]
        model = name
        model = assure_item(model)

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
    # print(f"copy items into {ITEMS_DST}")
    for item in items:
        # print("copy", item)
        shutil.copy(f"{ITEMS_SRC}/{item}.json", ITEMS_DST)

    TEXTURES_DST = f"{to}/assets/minecraft/textures/item"
    TEXTURES_SRC = f"{frm}/assets/minecraft/textures/item"
    os.makedirs(TEXTURES_DST, exist_ok=True)
    # print(f"copy textures into {TEXTURES_DST}")
    for texture in textures:
        # print("copy", texture)
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
    subprocess.check_call(["zip", "-rq", target, "."])
    os.chdir("..")


def ready(all_models):
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)

    shutil.rmtree("build", ignore_errors=True)
    generate_wheat_seeds(all_models)
    copy_files("generated", ["wheat_seeds"])


def finish(PACK_NAME, PACK_DESC):
    # make `pack.mcmeta`
    write_mcmeta(PACK_DESC)
    # rename `build` to pack name and zip
    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    zip(PACK_NAME)

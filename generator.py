import os
import json
import subprocess
import shutil

TARGET_DIR = "generated"
ITEM_DIR = f"{TARGET_DIR}/assets/minecraft/models/item"


def write_item(data, name):
    path = os.path.join(
        ITEM_DIR, f"{name}.json")
    json.dump(data, open(path, "w"), indent=2)
    print(f"wrote {name}")


def cactus_models(models={}):
    models[500] = "cactus_arm"
    models[501] = "cactus_flower"
    models[502] = "cactus_flower2"
    return models


def generate_wheat_seeds(models):
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    os.makedirs(ITEM_DIR)

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
    for item in items:
        shutil.copy(f"{ITEMS_SRC}/{item}.json", ITEMS_DST)

    TEXTURES_DST = f"{to}/assets/minecraft/textures/item"
    TEXTURES_SRC = f"{frm}/assets/minecraft/textures/item"
    os.makedirs(TEXTURES_DST, exist_ok=True)
    for texture in textures:
        shutil.copy(f"{TEXTURES_SRC}/{texture}.png", TEXTURES_DST)


def build_cactus_pack():
    PACK_NAME = "cactus"
    PACK_DESC = "Cactus Arm and Flowers"

    shutil.rmtree("build", ignore_errors=True)
    copy_files(
        "common",
        ["cactus_arm", "cactus_flower", "cactus_flower2"],
        ["cactus_flower", "cactus_flower2"])

    models = cactus_models()
    generate_wheat_seeds(models)
    copy_files("generated", ["wheat_seeds"])

    # make `pack.mcmeta`
    mcmeta = {
        "pack": {
            "pack_format": 7,
            "description": PACK_DESC
        }
    }
    json.dump(mcmeta, open("build/pack.mcmeta", "w"), indent=2)

    shutil.rmtree(PACK_NAME, ignore_errors=True)
    shutil.move("build", PACK_NAME)
    os.chdir(PACK_NAME)
    subprocess.check_call(f"zip -r ../{PACK_NAME}.zip .", shell=True)
    os.chdir("..")


if __name__ == '__main__':
    build_cactus_pack()

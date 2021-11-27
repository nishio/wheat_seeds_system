import reference
import pack
PACK_NAME = "umbrella"
DESCRIPTION = "Umbrella"
TO_EXCLUDE_FROM_ALLINONE = False

TEXTURES = {
    "white": "white_triangle",
    "red": "red_triangle",
}


def model_refs(models={}):
    reference.make_variation(700, "umbrella_up", TEXTURES, models)
    reference.make_variation(720, "umbrella_down", TEXTURES, models)
    return models


def main():
    models = model_refs({})
    pack.make_variation_modelfiles(
        "umbrella_up",
        "item/umbrella_up",
        "0", TEXTURES
    )
    pack.make_variation_modelfiles(
        "umbrella_down",
        "item/umbrella_down",
        "0", TEXTURES
    )
    pack.copy_files("generated", models.values(), [])
    pack.copy_files(
        "common", ["umbrella_up", "umbrella_down"],
        TEXTURES.values())

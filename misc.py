import pack
import reference
PACK_NAME = "misc"
DESCRIPTION = "Misc Wheat Seeds System"
TO_EXCLUDE_FROM_ALLINONE = False
MODELS = [
    "hole_grass_block", "hole_dirt",
]
TEXTURES = []


def model_refs(models={}):
    return reference.add(2000, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)

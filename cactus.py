import pack
import reference

MODELS = ["cactus_arm", "cactus_flower", "cactus_flower2"]
TEXTURES = ["cactus_flower", "cactus_flower2"]


def model_refs(models={}):
    return reference.add(500, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)


def build(all_models):
    PACK_NAME = "cactus"
    PACK_DESC = "Cactus Arm and Flowers"

    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

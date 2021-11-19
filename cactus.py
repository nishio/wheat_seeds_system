import pack


def model_refs(models={}):
    models[500] = "cactus_arm"
    models[501] = "cactus_flower"
    models[502] = "cactus_flower2"
    return models


TEXTURES = ["cactus_flower", "cactus_flower2"]


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)


def build(all_models):
    PACK_NAME = "cactus"
    PACK_DESC = "Cactus Arm and Flowers"

    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

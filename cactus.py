import pack
import reference
PACK_NAME = "cactus"
DESCRIPTION = "Cactus Arm and Flowers"
MODELS = ["cactus_arm", "cactus_flower", "cactus_flower2"]
TEXTURES = ["cactus_flower", "cactus_flower2"]


def model_refs(models={}):
    return reference.add(500, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)

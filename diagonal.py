import reference
import pack
import textures

PACK_NAME = "diagonal"
DESCRIPTION = "Diagonal Blocks"
IS_EXPERIMENTAL = False

BASES = ["diagonal1", "diagonal2",
         "diagonal3", "diagonal4", "diagonal5"]


def model_refs(models={}):
    sections = zip(range(800, 900, 20), BASES)
    for offset, name in sections:
        reference.make_variation(
            offset, name, textures.WOOL_TEXTURES, models)
    return models


def main():
    models = model_refs({})

    for base in BASES:
        pack.make_variation_modelfiles(
            base,
            f"item/{base}",
            "0", textures.WOOL_TEXTURES
        )

    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", BASES, [])

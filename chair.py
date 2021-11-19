import pack
import textures
import reference
PACK_NAME = "chairs"
DESCRIPTION = "Colorful Chairs"


def model_refs(models={}):
    sections = [
        (100, "round_chair"),
        (120, "chair"),
        (140, "tall_chair"),
        (160, "chair_with_desk"),
        (180, "chair_with_arm"),
    ]
    for offset, name in sections:
        reference.make_variation(
            offset, name, textures.WOOL_TEXTURES, models)
    return models


def main():
    models = model_refs({})
    BASES = ["round_chair", "chair", "tall_chair",
             "chair_with_desk", "chair_with_arm"]

    for base in BASES:
        pack.make_variation_modelfiles(
            base,
            f"item/{base}",
            "seat", textures.WOOL_TEXTURES
        )

    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", BASES, ["black", "mesh"])


def build(all_models):
    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

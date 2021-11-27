import pack
import reference
PACK_NAME = "invisible_holes"
DESCRIPTION = "Invisible Holes"
TO_EXCLUDE_FROM_ALLINONE = False
MODELS = [
    "hole_dirt", "hole_cobblestone",
]
TEXTURES = []


def model_refs(models={}):
    return reference.add(1300, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)

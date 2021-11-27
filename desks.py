import pack
import reference
PACK_NAME = "desks"
DESCRIPTION = "Desks"
IS_EXPERIMENTAL = False
MODELS = ["glass_table_1x1", "glass_table_3x2", "pc_table_4x2"]
TEXTURES = []


def model_refs(models={}):
    return reference.add(1000, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)

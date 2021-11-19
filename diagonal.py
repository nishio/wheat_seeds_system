import reference
import pack

PACK_NAME = "diagonal"
DESCRIPTION = "Diagonal Blocks"
IS_EXPERIMENTAL = True


def model_refs(models={}):
    return reference.add(
        800, models,
        ["diagonal1", "diagonal2",
         "diagonal3", "diagonal4", "diagonal5"])


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), [])

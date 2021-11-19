import reference
import pack

PACK_NAME = "lights"
DESCRIPTION = "Decoration Lights"
IS_EXPERIMENTAL = False


def model_refs(models={}):
    models = reference.add(
        900, models,
        [f"decolight{i + 1}" for i in range(9)])

    return reference.add(
        910, models,
        [f"ceil_light{i + 1}" for i in range(4)] + ["ceil_light_cloud"])


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), [])

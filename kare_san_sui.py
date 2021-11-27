import pack
import reference
PACK_NAME = "kare_san_sui"
DESCRIPTION = "KareSanSui Japanese Traditional Sand Garden"
TO_EXCLUDE_FROM_ALLINONE = False
MODELS = [
    "kss_1x1_straight", "kss_1x1_curve",
    "kss_2x2_straight", "kss_2x2_curve", "kss_2x2_circle",
    "kss_3x3_straight", "kss_3x3_circle"]
TEXTURES = MODELS


def model_refs(models={}):
    return reference.add(1200, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)

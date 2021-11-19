import pack
import reference

MODELS = [
    "macbook",
    "desktop",
    "monitor",
    "keyboard",
    "ipad"
]

TEXTURES = [
    "black", "desktop", "keyboard",
    "macbook", "monitor_arm", "monitor_frame", "white"]


def model_refs(models={}):
    return reference.add(600, models, MODELS)


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)


def build(all_models):
    PACK_NAME = "laptop"
    PACK_DESC = "Laptop, Desktop and Keyboard"

    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

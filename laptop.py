import pack


def model_refs(models={}):
    models[600] = "macbook"
    models[601] = "desktop"
    models[602] = "monitor"
    # models[603] = "large_monitor"
    # models[604] = "wall_monitor"
    models[603] = "keyboard"
    models[604] = "ipad"
    return models


TEXTURES = [
    "black", "desktop", "keyboard",
    "macbook", "monitor_arm", "monitor_frame", "white"]


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), TEXTURES)


def build(all_models):
    PACK_NAME = "laptop"
    PACK_DESC = "Laptop, Desktop and Keyboard"

    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

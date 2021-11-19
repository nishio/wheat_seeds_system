import reference
import pack


def model_refs(models={}):
    return reference.add(
        800, models,
        ["diagonal1", "diagonal2",
         "diagonal3", "diagonal4", "diagonal5"])


def main():
    models = model_refs({})
    pack.copy_files("common", models.values(), [])


def build(all_models):
    # it is experimental pack, so it is not included in all-in-one pack
    PACK_NAME = "diagonal"
    PACK_DESC = "Diagonal Blocks"
    pack.ready(all_models)
    main()
    pack.finish(PACK_NAME, PACK_DESC)

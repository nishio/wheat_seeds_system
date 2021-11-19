import cactus
import os
import json
import subprocess
import shutil
import pack
import laptop
import chair
import reference

# model refernce definitions


UMBRELLA_TEXTURES = {"white": "white_triangle",
                     "red": "red_triangle"}


def umbrella_model_refs(models={}):
    reference.make_variation(700, "umbrella_up", UMBRELLA_TEXTURES, models)
    reference.make_variation(720, "umbrella_down", UMBRELLA_TEXTURES, models)
    return models


def add_model_refs(offset, refs, models):
    for i, ref in enumerate(refs):
        id = offset + i
        assert id not in models
        models[id] = ref
    return models


def diagonal_model_refs(models={}):
    return add_model_refs(
        800,
        ["diagonal1", "diagonal2",
         "diagonal3", "diagonal4", "diagonal5"], models)


def all_model_refs():
    models = {}
    models = cactus.model_refs(models)
    models = laptop.model_refs(models)
    models = chair.model_refs(models)
    models = umbrella_model_refs(models)
    models = diagonal_model_refs(models)
    return models


def build_umbrella(all_models):
    PACK_NAME = "umbrella"
    PACK_DESC = "Umbrella"
    pack.ready(all_models)
    models = umbrella_model_refs({})
    pack.make_variation_modelfiles(
        "umbrella_up",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.make_variation_modelfiles(
        "umbrella_down",
        "item/umbrella_down",
        "0", UMBRELLA_TEXTURES
    )
    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", ["umbrella_up", "umbrella_down"],
                    UMBRELLA_TEXTURES.values())

    pack.finish(PACK_NAME, PACK_DESC)


def build_diagonal(all_models):
    # it is experimental pack, so it is not included in all-in-one pack
    PACK_NAME = "diagonal"
    PACK_DESC = "Diagonal Blocks"
    pack.ready(all_models)
    models = diagonal_model_refs({})
    pack.copy_files("common", models.values(), [])

    pack.finish(PACK_NAME, PACK_DESC)


def build_all_in_one_pack(all_models):
    PACK_NAME = "all-in-one"
    PACK_DESC = "All-in-one Wheat Seeds System"
    pack.ready(all_models)

    cactus.main()
    laptop.main()
    chair.main()

    # umbrella
    models = umbrella_model_refs({})
    pack.make_variation_modelfiles(
        "umbrella_up",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.make_variation_modelfiles(
        "umbrella_down",
        "item/umbrella_up",
        "0", UMBRELLA_TEXTURES
    )
    pack.copy_files("generated", models.values(), [])
    pack.copy_files("common", ["umbrella_up", "umbrella_down"],
                    UMBRELLA_TEXTURES.values())
    # end
    pack.finish(PACK_NAME, PACK_DESC)


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)


def main():
    all_models = all_model_refs()
    cactus.build(all_models)
    laptop.build(all_models)
    chair.build(all_models)
    build_umbrella(all_models)
    build_diagonal(all_models)
    build_all_in_one_pack(all_models)


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

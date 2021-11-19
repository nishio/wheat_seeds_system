import cactus
import os
import json
import subprocess
import shutil
import pack
import laptop
import chair
import reference
import umbrella
import diagonal


def all_model_refs():
    models = {}
    models = cactus.model_refs(models)
    models = laptop.model_refs(models)
    models = chair.model_refs(models)
    models = umbrella.model_refs(models)
    models = diagonal.model_refs(models)
    return models


def build_all_in_one_pack(all_models):
    PACK_NAME = "all-in-one"
    PACK_DESC = "All-in-one Wheat Seeds System"
    pack.ready(all_models)

    cactus.main()
    laptop.main()
    chair.main()
    umbrella.main()
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


def build(module):
    pack.ready(all_models)
    module.main()
    pack.finish(module.PACK_NAME, module.DESCRIPTION)


def main():
    global all_models
    all_models = all_model_refs()
    build(cactus)
    build(laptop)
    build(chair)
    umbrella.build(all_models)
    diagonal.build(all_models)
    build_all_in_one_pack(all_models)


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

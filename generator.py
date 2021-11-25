import cactus
import pack
import laptop
import chair
import umbrella
import diagonal
import lights
import misc
all_modules = [cactus, laptop, chair, umbrella, diagonal, lights, misc]


def all_model_refs():
    models = {}
    for m in all_modules:
        models = m.model_refs(models)
    return models


def build_all_in_one_pack(all_models):
    PACK_NAME = "all-in-one"
    PACK_DESC = "All-in-one Wheat Seeds System"
    pack.ready(all_models)
    for m in all_modules:
        if not m.IS_EXPERIMENTAL:
            m.main()

    pack.finish(PACK_NAME, PACK_DESC)


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)


def build(module, all_models):
    pack.ready(all_models)
    module.main()
    pack.finish(module.PACK_NAME, module.DESCRIPTION)


def main():
    all_models = all_model_refs()
    for m in all_modules:
        build(m, all_models)
    build_all_in_one_pack(all_models)


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

import cactus
import pack
import laptop
import chair
import umbrella
import diagonal
import lights
import books
import desks
import misc
import kare_san_sui
all_modules = [cactus, laptop, chair, umbrella,
               diagonal, lights, books, desks, kare_san_sui, misc]


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
        if not m.TO_EXCLUDE_FROM_ALLINONE:
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
    toc()


def toc():
    "table of contents"
    toc = []  # start, end, desc, models
    for m in all_modules:
        models = m.model_refs({})
        toc.append((min(models), max(models), m.DESCRIPTION, models))
    fo = open("toc.md", "w")
    fo.write("# Wheat Seeds System Index\n")
    for (start, end, desc, models) in sorted(toc):
        fo.write(f"\n## {desc}({start}-{end})\n\n")
        for k in sorted(models):
            name = models[k]
            fo.write(f"* {k}: {name}\n")
    fo.close()


if __name__ == "__main__":
    import sys
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()

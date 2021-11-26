import pack
import textures
import reference
PACK_NAME = "books"
DESCRIPTION = "Books"
IS_EXPERIMENTAL = False

SIMPLE_COVER_TEXTURE = {
    str(i): f"simple_book_cover/{i}" for i in range(10)}
COVER_TEXTURE = {
    str(i): f"book_cover/{i}" for i in range(10)}


def model_refs(models={}):
    sections = [
        (1100, "simple_book"),
        (1110, "book"),
    ]
    reference.make_variation(
        1100, "simple_book", SIMPLE_COVER_TEXTURE, models)
    reference.make_variation(
        1110, "book", COVER_TEXTURE, models)

    return models


def main():
    models = model_refs({})
    BASES = ["book", "simple_book"]

    pack.make_variation_modelfiles(
        "simple_book", "item/simple_book",
        "cover",
        SIMPLE_COVER_TEXTURE)
    pack.make_variation_modelfiles(
        "book", "item/book",
        "cover",
        COVER_TEXTURE)

    pack.copy_files("generated", models.values(), [])
    TEXTURES = (
        list(SIMPLE_COVER_TEXTURE.values()) +
        list(COVER_TEXTURE.values()))
    pack.copy_files("common", BASES, TEXTURES)

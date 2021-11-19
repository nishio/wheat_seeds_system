def make_variation(offset, prefix, texture_map, models):
    """
    Creates a references from texture map.
    """
    for id, k in enumerate(texture_map):
        name = f"{prefix}_{k}"
        assert offset + id not in models
        models[offset + id] = name

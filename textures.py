COLORS = "white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black".split()
assert len(COLORS) == 16
# 0:white 1:orange 2:magenta 3:light_blue 4:yellow 5:lime 6:pink 7:gray 8:light_gray
# 9:cyan 10:purple 11:blue 12:brown 13:green 14:red 15:black


def wool(color):
    return f"block/{color}_wool"


WOOL_TEXTURES = {c: wool(c) for c in COLORS}

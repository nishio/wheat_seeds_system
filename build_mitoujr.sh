# generate server resourcepacks for private multiplayer servers
# currently works on NISHIO's local environment
#
# Requires the per-pack output to already exist (run `python3 generator.py` first,
# which builds all-in-one/ and the individual packs).
set -e

# mitoujr = TransportPipes pack + all-in-one Wheat Seeds System
rm -rf build
mkdir build
cp -r TransportPipes/* build
cp -r all-in-one/* build

# Modernize to the Minecraft 1.21.4+ item-model format.
# The classic generator emits the pre-1.21.4 layout (pack_format 7 +
# `overrides`/`custom_model_data` predicates). Since 1.20.5 item NBT became
# components, and 1.21.4 replaced model `overrides` with item definitions
# (assets/minecraft/items/<item>.json, range_dispatch), the classic packs
# stop rendering on modern clients. modernize/migrate.py converts them.
# See modernize/README.md.
PACK_FORMAT="${PACK_FORMAT:-84}"   # 84 = MC 26.1.2; change to your target's resource format
python3 modernize/migrate.py --in build --out mitoujr.zip --pack-format "$PACK_FORMAT"

# Offline-validate the result against a vanilla client jar (no client launch
# needed): flatten every rendered model and catch unresolved/missing textures
# and mixed-atlas bake failures before deploying.
python3 modernize/validate_pack.py mitoujr.zip

# sha1 (set this as resource-pack-sha1 in server.properties)
shasum mitoujr.zip
mv mitoujr.zip ~/Dropbox
rm -r build

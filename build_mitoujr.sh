# generate server resourcepacks for private multiplayer servers
# currently works on NISHIO's local environment

# mitoujr
mkdir build
cp -r TransportPipes/* build
cp -r all-in-one/* build

cd build
zip -qr ../mitoujr.zip .
cd ..
rm -r build

# sha1
shasum mitoujr.zip
mv mitoujr.zip ~/Dropbox

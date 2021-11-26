read -p "tagname: " tagname
echo "Releasing $tagname"
gh release create $tagname *.zip
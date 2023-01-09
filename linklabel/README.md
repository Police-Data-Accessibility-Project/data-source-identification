# linklabel
Automatically generate labels for URLs from a library of regular expressions.

# building
```
# clone repo with submodules(!)
git clone --recursive https://github.com/Police-Data-Accessibility-Project/data-source-identification

# create build directory
mkdir linklabelbuild

# enter dir
cd linklabelbuild

# geneate build
cmake -G "Unix Makefiles" ../data-source-identification/linklabel

# build it
make
```

You should now have succesfully built `linklabel`. Good job!

# usage
To use `linklabel`; place your regular expressions as separate files in directory `./regexes/` alongside the linklabel library. Then just run the binary and feed it URLs on separate lines.

Still inside of the build directory:
```
# create regex library
mkdir regexes

# add two example regexes
echo "news" > regexes/news
echo "transgender" > regexes/trans

# feed linklabel a URL
echo "https://police.gov/news/example-transgender-entry" | ./linklabel | jq
```

If all goes well, you should see something similar to the following output:
```
{
  "labels": [
    "news",
    "trans"
  ],
  "url": "https://police.gov/news/example-transgender-entry"
}
```

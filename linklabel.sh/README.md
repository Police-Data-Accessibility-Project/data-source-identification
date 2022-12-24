# linklabel.sh
The slower not recommended(!) bash version prototype of linklabel.

Not recommended for use. Here for historical reasons and because it might still be useful to someone if they can't get the other one to work.

# usage
First create a directory called `regexes` next to the script.
Then put any regexes you want to search the URLs for in separate files in that directory.
(It's okay to use subdirectories as well! The script recursively searches through `./regexes` for regular files.)
Then just run the script and feed it URLs on a line by line basis...

It will spit out JSON objects so use `jq` for viewing purposes.

```
echo "https://police.gov/news/example-entry" | ./linklabel.sh | jq
```

It's recommended to use GNU `parallel` to run this script and speed up processing to a modest speed.
**Just use the C++ version of linklabel. It's easily 1500 times faster.**

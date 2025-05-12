import os
import sys
import json
from transformers import pipeline

def main():
    urls = json.loads(sys.stdin.read())

    pipe = pipeline("text-classification", model="PDAP/url-relevance")
    results = pipe(urls)

    print("Executable:", sys.executable, file=sys.stderr)
    print("sys.path:", sys.path, file=sys.stderr)
    print("PYTHONPATH:", os.getenv("PYTHONPATH"), file=sys.stderr)

    if len(results) != len(urls):
        raise RuntimeError(f"Expected {len(urls)} results, got {len(results)}")
    bools = [r["score"] >= 0.5 for r in results]

    print(json.dumps(bools))

if __name__ == "__main__":
    main()

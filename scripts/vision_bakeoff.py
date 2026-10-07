"""Score the local-vision model lane on reading plans dimensions (Block 2 bake-off).

Usage: python scripts/vision_bakeoff.py <endpoint> <out.json>
Pages come from $LONGEZ_SCAN_PAGES (default ~/.cache/long-ez/scan-1980/pages). Requests run
one at a time: the vision server shares a RAM-bound node.
"""

import base64
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import yaml

MODEL = (
    "mlx-community/Qwen3-VL-8B-Instruct-4bit"  # roster local-vision, checked 2026-10-01
)
PROMPT = (
    "This is a page from 1980 homebuilt aircraft construction plans. Read the printed and "
    "hand-lettered dimensions on the drawing. {q} Answer with the numbers as printed, then "
    "one short phrase saying where on the page you read them."
)
NUM = re.compile(r"-?\d+(?:\.\d+)?|-?\.\d+")
PREFIX = re.compile(
    r"\b(?:F\.?\s?S|W\.?\s?L|B\.?\s?L)\.?\s*", re.IGNORECASE
)  # "FS.17" is 17, not .17


def ask(endpoint, img, q):
    b64 = base64.b64encode(img.read_bytes()).decode()
    body = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                    {"type": "text", "text": PROMPT.format(q=q)},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/chat/completions",
        json.dumps(body).encode(),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["choices"][0]["message"]["content"] or ""


def parse_numbers(ans):
    return [
        float(x)
        for x in NUM.findall(PREFIX.sub(" ", ans).replace(",", " ").replace("½", ".5"))
    ]


def score_value(truth, nums):
    if any(abs(n - truth) < 1e-6 for n in nums):
        return "exact"
    if any(abs(n - truth) <= max(0.05 * abs(truth), 0.1) for n in nums):
        return "near"
    return "wrong"


def main():
    endpoint, out = sys.argv[1], Path(sys.argv[2])
    pages = Path(
        os.environ.get("LONGEZ_SCAN_PAGES", "~/.cache/long-ez/scan-1980/pages")
    ).expanduser()
    items = yaml.safe_load(
        (Path(__file__).parent / "vision_bakeoff_truth.yaml").read_text()
    )["items"]
    rows, tally = [], {"exact": 0, "near": 0, "wrong": 0}
    for it in items:
        t0 = time.time()
        try:
            ans = ask(endpoint, pages / f"{it['page']:03d}.jpg", it["q"])
        except (
            OSError,
            ValueError,
            KeyError,
        ) as e:  # a lane failure is a scored miss, and it is recorded
            ans = f"ERROR {e}"
        nums = parse_numbers(ans)
        verdicts = [score_value(t, nums) for t in it["truth"]]
        for v in verdicts:
            tally[v] += 1
        rows.append(
            {
                **it,
                "answer": ans,
                "verdicts": verdicts,
                "secs": round(time.time() - t0, 1),
            }
        )
        print(
            f"{it['id']:14} {' '.join(verdicts):30} {rows[-1]['secs']:6}s  {ans[:90]!r}",
            flush=True,
        )
    n = sum(tally.values())
    summary = {**tally, "values": n, "exact_rate": round(tally["exact"] / n, 3)}
    out.write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=1)
    )  # raw answers quote plans text: keep out of the repo
    print(json.dumps(summary))
    if any(r["answer"].startswith("ERROR") for r in rows):
        sys.exit(2)  # fail loud: a dead lane must not read as a low score


if __name__ == "__main__":
    main()

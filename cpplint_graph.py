import subprocess
import re
import os
from collections import defaultdict
import matplotlib.pyplot as plt

LINE_RE = re.compile(r'^(.*?):(\d+):\s+(.*?)\s+\[(.*?)\]\s+\[(\d+)\]')


def collect_files():
    paths = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith((".cc", ".cpp", ".h", ".hpp")):
                paths.append(os.path.join(root, f))
    return paths


def run_cpplint(paths):
    cmd = ["python3", "-m", "cpplint"] + paths
    result = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    return (result.stderr + result.stdout).splitlines()


def parse(lines):
    by_category = defaultdict(int)
    by_file = defaultdict(int)
    by_severity = defaultdict(int)

    for line in lines:
        m = LINE_RE.match(line)
        if not m:
            continue

        file_path, _, _, category, severity = m.groups()

        by_category[category] += 1
        by_file[file_path] += 1
        by_severity[int(severity)] += 1

    return by_category, by_file, by_severity


def plot_bar(data, title, top_n=10):
    items = sorted(data.items(), key=lambda x: -x[1])[:top_n]
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    plt.figure(figsize=(10, 5))
    plt.barh(labels[::-1], values[::-1])
    plt.title(title)
    plt.xlabel("Count")
    plt.tight_layout()
    plt.show()


def plot_severity(by_severity):
    labels = sorted(by_severity.keys())
    values = [by_severity[k] for k in labels]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values)
    plt.title("Errors by Severity")
    plt.xlabel("Severity")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("Collecting files...")
    paths = collect_files()
    print(f"Found {len(paths)} files")

    if not paths:
        print("No C++ files found.")
        exit(1)

    # LIMIT TO 100 FILES
    paths = paths[:100]
    print(f"Analyzing {len(paths)} files")

    print("Running cpplint...")
    lines = run_cpplint(paths)

    print("Parsing results...")
    by_category, by_file, by_severity = parse(lines)

    if not by_category:
        print("No cpplint errors found")
        exit(0)

    print("Generating charts...")

    # TOP 20 ERROR CATEGORIES
    top_20_categories = dict(
        sorted(by_category.items(), key=lambda x: -x[1])[:20]
    )

    plot_bar(top_20_categories, "Top cpplint Error Categories")

    plot_severity(by_severity)

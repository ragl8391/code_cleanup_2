import subprocess
import re
import os
from collections import defaultdict
import matplotlib.pyplot as plt

# Example cppcheck format enforced:
# file:line: severity: message [id]

LINE_RE = re.compile(r'^(.*?):(\d+):\s+(\w+):\s+(.*?)\s+\[(.*?)\]')


def collect_files():
    paths = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith((".cc", ".cpp", ".h", ".hpp")):
                paths.append(os.path.join(root, f))
    return paths


def run_cppcheck(paths):
    cmd = [
        "cppcheck",
        "--enable=all",
        "--inline-suppr",
        "--quiet",
        "--template={file}:{line}: {severity}: {message} [{id}]"
    ] + paths

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # cppcheck writes most output to stderr
    return (result.stderr + result.stdout).splitlines()


def parse(lines):
    by_id = defaultdict(int)
    by_file = defaultdict(int)
    by_severity = defaultdict(int)

    for line in lines:
        m = LINE_RE.match(line)
        if not m:
            continue

        file_path, _, severity, _, msg_id = m.groups()

        by_id[msg_id] += 1
        by_file[file_path] += 1
        by_severity[severity] += 1

    return by_id, by_file, by_severity


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
    order = ["error", "warning", "style", "performance", "portability", "information"]

    labels = [k for k in order if k in by_severity] + [
        k for k in by_severity if k not in order
    ]
    values = [by_severity[k] for k in labels]

    plt.figure(figsize=(7, 4))
    plt.bar(labels, values)
    plt.title("cppcheck Messages by Severity")
    plt.xlabel("Severity")
    plt.ylabel("Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("Collecting files...")
    paths = collect_files()
    print(f"Found {len(paths)} files")

    if not paths:
        print("No C++ files found.")
        exit(1)

    # limit for speed (same idea as your script)
    paths = paths[:100]
    print(f"Analyzing {len(paths)} files")

    print("Running cppcheck...")
    lines = run_cppcheck(paths)

    print("Parsing results...")
    by_id, by_file, by_severity = parse(lines)

    if not by_id:
        print("No cppcheck issues found")
        exit(0)

    print("Generating charts...")

    # Top issue IDs
    top_20_ids = dict(sorted(by_id.items(), key=lambda x: -x[1])[:20])
    plot_bar(top_20_ids, "Top cppcheck Issue IDs")

    # Severity distribution
    plot_severity(by_severity)

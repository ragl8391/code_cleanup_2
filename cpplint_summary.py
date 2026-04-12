import subprocess
import re
import os
from collections import defaultdict

# Regex to parse cpplint output lines
# Example:
# path/to/file.cc:123:  Missing space before {  [whitespace/braces] [5]
LINE_RE = re.compile(r'^(.*?):(\d+):\s+(.*?)\s+\[(.*?)\]\s+\[(\d+)\]')


def run_cpplint(paths):
    cmd = ["python3", "-m", "cpplint"] + paths
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    return result.stderr.splitlines()


def summarize(lines):
    by_category = defaultdict(int)
    by_file = defaultdict(int)
    by_severity = defaultdict(int)

    for line in lines:
        match = LINE_RE.match(line)
        if not match:
            continue

        file_path, line_no, message, category, severity = match.groups()

        by_category[category] += 1
        by_file[file_path] += 1
        by_severity[int(severity)] += 1

    return by_category, by_file, by_severity


def print_summary(by_category, by_file, by_severity):
    print("\n=== Errors by Category ===")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"{cat:30} {count}")

    print("\n=== Errors by File ===")
    for f, count in sorted(by_file.items(), key=lambda x: -x[1])[:20]:
        print(f"{f:50} {count}")

    print("\n=== Errors by Severity ===")
    for sev, count in sorted(by_severity.items()):
        print(f"Severity {sev}: {count}")


if __name__ == "__main__":
    # Change to your repo paths
    paths = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith((".cc", ".cpp", ".h", ".hpp")):
                paths.append(os.path.join(root, f))

    print(f"Found {len(paths)} files")
    lines = run_cpplint(paths)

    by_category, by_file, by_severity = summarize(lines)
    print_summary(by_category, by_file, by_severity)

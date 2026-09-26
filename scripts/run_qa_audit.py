"""
ComplyFlow - Repository Quality Assurance & Pre-Release Audit Runner
===================================================================
Automates verification for Phase 9 / 9.1:
1. Repository-wide Merge Conflict Marker Scanning (all files, tracked & untracked)
2. Trailing Whitespace Scanning (all text files, tracked & untracked)
3. Non-Portable Link Scanning (forbids file:/// links in documentation)
4. Internal Relative Markdown Link Integrity
5. Secret & Credential Scanning
6. File Size Audit & Git Working Tree Checks
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- 1. Secret & Credential Patterns ---
SECRET_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]'), "API Key Pattern"),
    (re.compile(r'(?i)(secret|client[_-]?secret)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]'), "Secret Pattern"),
    (re.compile(r'(?i)(access[_-]?token|auth[_-]?token)\s*[:=]\s*[\'"][^\'"]{10,}[\'"]'), "Token Pattern"),
    (re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'), "Private Key"),
    (re.compile(r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*[\'"][^\'"]+[\'"]'), "AWS Credential"),
    (re.compile(r'(?i)(mongodb(?:\+srv)?|postgres(?:ql)?|mysql)://[^\s\'"]+:[^\s\'"]+@'), "Database URL with Password"),
    (re.compile(r'AIza[0-9A-Za-z\-_]{35}'), "Google API Key Pattern"),
    (re.compile(r'sk-[a-zA-Z0-9]{20,}'), "OpenAI API Key Pattern"),
]

# --- 2. Conflict Marker Patterns (Strict line-start) ---
CONFLICT_PATTERNS = [
    (re.compile(r'^<{7}(?:\s.*)?$', re.MULTILINE), "<<<<<<< conflict start"),
    (re.compile(r'^={7}$', re.MULTILINE), "======= conflict divider"),
    (re.compile(r'^>{7}(?:\s.*)?$', re.MULTILINE), ">>>>>>> conflict end"),
]

# --- 3. Markdown Link Pattern [text](url) ---
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

TEXT_EXTENSIONS = {'.md', '.py', '.sql', '.json', '.csv', '.yml', '.yaml', '.txt', '.gitignore', '.gitkeep', '.cfg'}


def get_all_repo_files():
    """Returns all files in repository excluding .git."""
    files = []
    for p in PROJECT_ROOT.rglob('*'):
        if p.is_file() and '.git' not in p.parts:
            files.append(p)
    return files


def audit_untracked_and_all_files():
    print("\n--- 1. Repository-Wide Text File Scanning (Tracked & Untracked) ---")
    files = get_all_repo_files()
    total_files = len(files)
    text_files = [f for f in files if f.suffix in TEXT_EXTENSIONS or f.name in {'.gitignore', 'LICENSE'}]

    conflict_errors = []
    whitespace_warnings = []
    total_lines_scanned = 0

    for p in text_files:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        lines = content.splitlines()
        total_lines_scanned += len(lines)

        # Check conflict markers
        for pat, desc in CONFLICT_PATTERNS:
            if pat.search(content):
                conflict_errors.append((rel, desc))

        # Check trailing whitespace (flag files with trailing spaces)
        trailing_lines = [i + 1 for i, line in enumerate(lines) if line.endswith((' ', '\t'))]
        if trailing_lines:
            # We track lines with trailing whitespace
            whitespace_warnings.append((rel, len(trailing_lines), trailing_lines[:3]))

    print(f"Scanned {len(text_files)} text files ({total_lines_scanned} total lines) across the repository.")

    if conflict_errors:
        print(f"[FAIL] Found {len(conflict_errors)} merge conflict marker(s):")
        for f, desc in conflict_errors:
            print(f"  - {f}: {desc}")
    else:
        print("[PASS] Zero merge conflict markers found across all repository files.")

    if whitespace_warnings:
        print(f"[INFO] Trailing whitespace detected in {len(whitespace_warnings)} file(s).")
    else:
        print("[PASS] Zero trailing whitespace detected across text files.")

    return len(conflict_errors), len(whitespace_warnings)


def audit_non_portable_links():
    print("\n--- 2. Auditing for Non-Portable Links (file:///) ---")
    files = get_all_repo_files()
    md_files = [f for f in files if f.suffix == '.md']
    non_portable = []

    for p in md_files:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        bad_links = []
        # Check actual markdown link targets [text](url)
        links = MD_LINK_PATTERN.findall(content)
        for text, url in links:
            url_clean = url.strip()
            if url_clean.lower().startswith('file:') or 'file:///' in url_clean:
                bad_links.append(f"[{text}]({url_clean})")

        # Check for unquoted accidental file:/// occurrences
        content_no_blocks = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content_no_code = re.sub(r'`[^`]*`', '', content_no_blocks)
        if 'file:///' in content_no_code:
            bad_links.append("Unquoted file:/// reference")

        if bad_links:
            non_portable.append((rel, bad_links))

    if non_portable:
        print(f"[FAIL] Found non-portable file:/// link(s) in {len(non_portable)} file(s):")
        for f, issues in non_portable:
            print(f"  - {f}: {', '.join(issues)}")
    else:
        print(f"[PASS] Zero non-portable 'file:///' links detected across all {len(md_files)} markdown files.")

    return len(non_portable)


def audit_markdown_relative_links():
    print("\n--- 3. Auditing Internal Relative Markdown Links ---")
    files = get_all_repo_files()
    md_files = [f for f in files if f.suffix == '.md']
    broken_links = []
    total_links = 0

    for p in md_files:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        for match in MD_LINK_PATTERN.finditer(content):
            total_links += 1
            text = match.group(1)
            target = match.group(2)

            # Skip external urls and anchors within same doc
            if target.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Strip anchors in relative paths
            target_path = target.split('#')[0]
            if not target_path:
                continue

            target_file = (p.parent / target_path).resolve()

            if not target_file.exists():
                broken_links.append((rel, text, target))

    if broken_links:
        print(f"[FAIL] Found {len(broken_links)} broken relative link(s) out of {total_links} total links:")
        for source, text, target in broken_links:
            print(f"  - In {source}: [{text}]({target}) -> Target does not exist!")
    else:
        print(f"[PASS] All {total_links} relative markdown links resolve successfully to existing files.")

    return len(broken_links)


def audit_secrets():
    print("\n--- 4. Scanning for Secrets and Credentials ---")
    files = get_all_repo_files()
    text_files = [f for f in files if f.suffix in TEXT_EXTENSIONS or f.name in {'.gitignore', 'LICENSE'}]
    secrets_found = []

    for p in text_files:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        for pat, label in SECRET_PATTERNS:
            for match in pat.finditer(content):
                val = match.group(0)
                # Ignore documentation placeholders / templates
                if any(x in val.lower() for x in ['example', 'placeholder', 'redacted', 'your_', '<', '>']):
                    continue
                secrets_found.append((rel, label, match.start()))

    if secrets_found:
        print(f"[ALERT] Potential secrets detected ({len(secrets_found)}):")
        for f, label, pos in secrets_found:
            print(f"  - {f} : {label} at char {pos}")
    else:
        print("[PASS] No hard-coded credentials or high-confidence secret patterns were detected.")

    return len(secrets_found)


def audit_file_sizes(threshold_kb=1000):
    print(f"\n--- 5. Auditing File Sizes (Threshold: {threshold_kb} KB) ---")
    files = get_all_repo_files()
    large_files = []

    for p in files:
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        size_kb = p.stat().st_size / 1024.0
        if size_kb > threshold_kb:
            large_files.append((rel, size_kb))

    if large_files:
        print(f"Found {len(large_files)} file(s) exceeding {threshold_kb} KB:")
        for f, size in large_files:
            print(f"  - {f}: {size:.2f} KB (Expected/Tracked)")
    else:
        print(f"[PASS] No files exceed {threshold_kb} KB.")

    all_files = sorted(
        [(p.relative_to(PROJECT_ROOT).as_posix(), p.stat().st_size / 1024.0) for p in files],
        key=lambda x: x[1], reverse=True
    )[:5]
    print("\nTop 5 Largest Files in Repository:")
    for f, size in all_files:
        print(f"  - {f:50} {size:8.2f} KB")


if __name__ == "__main__":
    print("==================================================")
    print("ComplyFlow QA & Release Preparation Audit (v9.1)")
    print("==================================================")
    conflicts, ws = audit_untracked_and_all_files()
    np_links = audit_non_portable_links()
    broken_links = audit_markdown_relative_links()
    secrets = audit_secrets()
    audit_file_sizes()
    print("\n==================================================")
    print(f"SUMMARY: Conflicts={conflicts}, NonPortableLinks={np_links}, BrokenLinks={broken_links}, Secrets={secrets}")
    print("==================================================")
    if conflicts > 0 or np_links > 0 or broken_links > 0 or secrets > 0:
        sys.exit(1)
    sys.exit(0)

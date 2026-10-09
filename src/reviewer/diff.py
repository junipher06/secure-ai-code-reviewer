"""Parse unified diffs as data. Never execute reviewed code."""

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from .errors import ReviewError


@dataclass
class Change:
    path: str
    added: list[tuple[int, str]] = field(default_factory=list)
    visible_lines: set[int] = field(default_factory=set)
    previous_path: str | None = None


def safe_path(path: str) -> str:
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or ".." in PurePosixPath(path).parts
        or any(ord(char) < 32 for char in path)
    ):
        raise ReviewError("Diff contains an unsupported or unsafe file path.")
    return path


def parse_diff(text: str, limit: int = 60000) -> list[Change]:
    if not text.strip() or len(text.encode("utf-8")) > limit:
        raise ReviewError("Diff is empty or too large; manual review needed.")
    changes: list[Change] = []
    current = None
    old = None
    line_no = 0
    in_hunk = False
    for line in text.splitlines():
        if line.startswith("diff --git "):
            current, old, in_hunk = None, None, False
        elif not in_hunk and line.startswith("--- "):
            old = line[4:]
            if old.startswith("a/"):
                old = safe_path(old[2:])
            elif old != "/dev/null":
                raise ReviewError("Unsupported diff path format.")
        elif not in_hunk and line.startswith("+++ "):
            new = line[4:]
            if new == "/dev/null":
                if not old or old == "/dev/null":
                    raise ReviewError("Invalid deleted-file diff.")
                new = old
            elif new.startswith("b/"):
                new = safe_path(new[2:])
            else:
                raise ReviewError("Unsupported diff path format.")
            current = Change(new, previous_path=old if old != "/dev/null" else None)
            changes.append(current)
        elif line.startswith("@@ "):
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if current is None or match is None:
                raise ReviewError("Invalid diff hunk.")
            line_no, in_hunk = int(match.group(1)), True
        elif in_hunk and current is not None:
            if line.startswith("+"):
                current.added.append((line_no, line[1:]))
                current.visible_lines.add(line_no)
                line_no += 1
            elif line.startswith(" "):
                current.visible_lines.add(line_no)
                line_no += 1
            elif line.startswith("-") or line.startswith("\\ No newline"):
                continue
            else:
                raise ReviewError("Unsupported diff hunk content.")
    if not changes or len({item.path for item in changes}) != len(changes):
        raise ReviewError("No reviewable text files or duplicate paths in diff.")
    return changes

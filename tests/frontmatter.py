from __future__ import annotations

from pathlib import Path


def frontmatter_for(path: Path) -> dict[str, str]:
    """Parse the small YAML frontmatter subset used by SKILL.md files.

    The tests intentionally stay dependency-free, but descriptions may use
    folded YAML scalars (``description: >-``), so a line-by-line ``key: value``
    split is not enough for the public load-trigger contract.
    """
    text = path.read_text(encoding="utf-8")
    _, frontmatter, _ = text.split("---\n", 2)
    lines = frontmatter.splitlines()
    data: dict[str, str] = {}
    index = 0

    while index < len(lines):
        line = lines[index]
        index += 1
        if ":" not in line or line.startswith((" ", "\t")):
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value in {">", ">-", "|", "|-"}:
            parts: list[str] = []
            while index < len(lines):
                continuation = lines[index]
                if continuation and not continuation.startswith((" ", "\t")):
                    break
                parts.append(continuation.strip())
                index += 1
            if value.startswith("|"):
                data[key] = "\n".join(parts).strip()
            else:
                data[key] = " ".join(part for part in parts if part).strip()
            continue

        data[key] = value.strip('"\'')

    return data

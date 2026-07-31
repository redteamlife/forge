"""Target adapters for forge_docs_export.py.

render(target, plan) -> {output_relpath: content}, deterministic. The security /
classification decisions live in forge_docs_export.py; adapters only shape the
kept pages for a target.

- obsidian (TASK-025): near-identity — preserve folders, frontmatter, body.
- gitlab-wiki (TASK-024): slug pages, preserve frontmatter (GitLab renders it),
  generate home.md and _sidebar.md from the README nav manifest, rewrite
  internal links to wiki slugs.
"""
from __future__ import annotations

import re
from pathlib import Path


def _slugify(name: str) -> str:
    base = re.sub(r"^\d+\s*[-_.]\s*", "", name)
    base = base.rsplit(".md", 1)[0]
    base = re.sub(r"[^\w./-]+", "-", base).strip("-")
    return base


def _page(entry: dict) -> str:
    fm = entry["fm"]
    body = entry["body"]
    if fm:
        return f"---{fm}---{body}"
    return body.lstrip("\n")


def obsidian(plan: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for e in plan["kept"]:
        out[e["src"]] = _page(e)
    return out


def _wiki_slug_for(src: str) -> str:
    parts = [_slugify(p) for p in Path(src).parts]
    return "/".join(parts)


def _rewrite_links(body: str, slug_by_name: dict[str, str]) -> str:
    def repl(m: "re.Match[str]") -> str:
        text, target = m.group(1), m.group(2)
        if "://" in target or target.startswith("#"):
            return m.group(0)
        path, _, anchor = target.partition("#")
        name = Path(path).name
        slug = slug_by_name.get(_slugify(name))
        if slug is None:
            return m.group(0)
        return f"[{text}]({slug}{('#' + anchor) if anchor else ''})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, body)


def _sidebar_from_readme(plan: dict, slug_by_name: dict[str, str]) -> str | None:
    readme = next((e for e in plan["kept"]
                   if Path(e["src"]).name.lower() == "readme.md"), None)
    if readme is None:
        return None
    lines = ["# Navigation", ""]
    for m in re.finditer(r"[-*]\s+\[([^\]]+)\]\(([^)]+)\)", readme["body"]):
        text, target = m.group(1), m.group(2)
        if "://" in target:
            continue
        slug = slug_by_name.get(_slugify(Path(target).name))
        if slug:
            lines.append(f"- [{text}]({slug})")
    return "\n".join(lines) + "\n" if len(lines) > 2 else None


def gitlab_wiki(plan: dict) -> dict[str, str]:
    slug_by_name: dict[str, str] = {}
    slug_by_src: dict[str, str] = {}
    seen: dict[str, str] = {}
    for e in plan["kept"]:
        slug = _wiki_slug_for(e["src"])
        if slug in seen and seen[slug] != e["src"]:
            raise ValueError(
                f"gitlab-wiki slug collision: {e['src']} and {seen[slug]} "
                f"both map to {slug}")
        seen[slug] = e["src"]
        slug_by_src[e["src"]] = slug
        slug_by_name[_slugify(Path(e["src"]).name)] = slug

    out: dict[str, str] = {}
    for e in plan["kept"]:
        name = Path(e["src"]).name.lower()
        body = _rewrite_links(e["body"], slug_by_name)
        page = f"---{e['fm']}---{body}" if e["fm"] else body.lstrip("\n")
        if name == "readme.md":
            out["home.md"] = page
        else:
            out[slug_by_src[e["src"]] + ".md"] = page

    sidebar = _sidebar_from_readme(plan, slug_by_name)
    if sidebar:
        out["_sidebar.md"] = sidebar
    return out


def render(target: str, plan: dict) -> dict[str, str]:
    if target == "obsidian":
        return obsidian(plan)
    if target == "gitlab-wiki":
        return gitlab_wiki(plan)
    raise ValueError(f"unknown target: {target}")

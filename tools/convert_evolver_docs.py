from __future__ import annotations

import argparse
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


TOPICS = {
    "datafile": "datafile.htm",
    "syntax": "syntax.htm",
    "elements": "elements.htm",
    "commands": "commands.htm",
    "single": "single.htm",
    "toggle": "toggle.htm",
    "constraints": "constrnt.htm",
    "quantities": "quants.htm",
    "energies": "energies.htm",
}


class MarkdownishHTMLParser(HTMLParser):
    SKIP_TAGS = {"script", "style"}
    BLOCK_TAGS = {
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "li",
        "ol",
        "p",
        "pre",
        "table",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.pending_ids: list[str] = []
        self.heading_level: int | None = None
        self.pre_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return

        if tag == "a" and attrs_dict.get("id"):
            self.pending_ids.append(attrs_dict["id"] or "")
            return

        heading_match = re.fullmatch(r"h([1-6])", tag)
        if heading_match:
            self.heading_level = int(heading_match.group(1))
            self.pending_ids = []
            self.parts.append("\n\n" + "#" * self.heading_level + " ")
            return

        if tag == "pre":
            self.pre_depth += 1
            self.parts.append("\n\n```text\n")
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            if tag in self.SKIP_TAGS:
                self.skip_depth -= 1
            return

        if re.fullmatch(r"h[1-6]", tag) and self.heading_level is not None:
            self.parts.append("\n")
            self.heading_level = None
            return

        if tag == "pre" and self.pre_depth:
            self.pre_depth -= 1
            self.parts.append("\n```\n")
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.pre_depth:
            self.parts.append(data)
            return

        collapsed = " ".join(data.split())
        if not collapsed:
            return
        if self._needs_space_before(collapsed):
            self.parts.append(" ")
        self.parts.append(collapsed)

    def _needs_space_before(self, text: str) -> bool:
        if not self.parts:
            return False
        previous = self.parts[-1]
        if not previous or previous.endswith(("\n", " ", "# ")):
            return False
        if text.startswith((".", ",", ":", ";", ")", "]", "}")):
            return False
        return True

    def text(self) -> str:
        text = unescape("".join(self.parts))
        lines = [line.rstrip() for line in text.splitlines()]
        compact: list[str] = []
        previous_blank = True
        in_fence = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                if not previous_blank:
                    compact.append("")
                compact.append(stripped)
                in_fence = not in_fence
                previous_blank = False
                continue

            if in_fence:
                compact.append(line)
                previous_blank = False
                continue

            if not stripped:
                if not previous_blank:
                    compact.append("")
                previous_blank = True
                continue

            compact.append(stripped)
            previous_blank = False

        return "\n".join(compact).strip()


def convert_html(html: str, *, keep_examples: bool = False) -> str:
    if not keep_examples:
        html = strip_examples(html)
    parser = MarkdownishHTMLParser()
    parser.feed(html)
    parser.close()
    text = parser.text()
    if not keep_examples:
        text = re.sub(r"\nExamples?:\s*(?=\n|$)", "\n", text)
    return text


def strip_examples(html: str) -> str:
    pre_re = re.compile(r"<pre\b[^>]*>.*?</pre>", re.IGNORECASE | re.DOTALL)

    def replace(match: re.Match[str]) -> str:
        prefix = convert_html(match.string[max(0, match.start() - 240) : match.start()], keep_examples=True)
        pre_text = convert_html(match.group(0), keep_examples=True)
        is_obvious_example = "example" in prefix.lower()
        is_large_sample = len(pre_text) > 1200
        return "" if is_obvious_example or is_large_sample else match.group(0)

    return pre_re.sub(replace, html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path, help="Directory containing Evolver HTML docs.")
    parser.add_argument("--out-dir", type=Path, default=Path("tools/docs"))
    parser.add_argument("--topic", action="append", choices=TOPICS, help="Topic to convert. May be repeated.")
    parser.add_argument("--keep-examples", action="store_true", help="Keep obvious examples and long samples.")
    args = parser.parse_args()

    topics = args.topic or list(TOPICS)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for topic in topics:
        source = args.source_dir / TOPICS[topic]
        if not source.is_file():
            raise SystemExit(f"Missing source page: {source}")
        html = source.read_text(encoding="utf-8", errors="replace")
        text = convert_html(html, keep_examples=args.keep_examples)
        output = args.out_dir / f"{topic}.md"
        output.write_text(text + "\n", encoding="utf-8")
        print(f"{source} -> {output}")


if __name__ == "__main__":
    main()

"""Конвертер REPORT.md -> .docx для отчётов по лабораторным.

Тонкий Markdown-парсер, покрывающий именно то, что мы кладём в REPORT.md:
заголовки (H1/H2/H3), горизонтальные линии, таблицы GFM (с выравниванием
`---:` / `:---:`), картинки `![](path)`, ограждённые ```-блоки кода,
маркированные/нумерованные списки, а также инлайновые `**bold**`,
`*italic*`, `` `code` ``.

Запуск:
    python render_report.py week3/REPORT.md
    # -> week3/Отчёт_Лабораторная_3_вариант5.docx  (имя берётся из --out
    #    или вычисляется из номера недели/варианта; см. main)

    python render_report.py week3/REPORT.md --out week3/custom.docx
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
CODE_RE = re.compile(r"`([^`]+?)`")
IMAGE_RE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")
LINK_RE = re.compile(r"\[([^\]]+?)\]\(([^)]+)\)")


def _add_inline(paragraph, text: str):
    """Разбирает **bold**, *italic*, `code`, [text](url) и добавляет их как runs.
    Порядок токенизации: сначала inline-код (нельзя вкладывать), затем bold, italic, ссылки."""
    tokens: list[tuple[str, str]] = []

    def tokenize(s: str, kind: str):
        if kind != "text":
            tokens.append((kind, s))
            return
        i = 0
        while i < len(s):
            m_code = CODE_RE.search(s, i)
            m_bold = BOLD_RE.search(s, i)
            m_ital = ITALIC_RE.search(s, i)
            m_link = LINK_RE.search(s, i)
            candidates = [m for m in (m_code, m_bold, m_ital, m_link) if m]
            if not candidates:
                tokens.append(("text", s[i:]))
                return
            m = min(candidates, key=lambda x: x.start())
            if m.start() > i:
                tokens.append(("text", s[i:m.start()]))
            if m is m_code:
                tokens.append(("code", m.group(1)))
            elif m is m_bold:
                for sub in re.split(r"(`[^`]+?`)", m.group(1)):
                    if sub.startswith("`") and sub.endswith("`"):
                        tokens.append(("bold_code", sub[1:-1]))
                    elif sub:
                        tokens.append(("bold", sub))
            elif m is m_ital:
                tokens.append(("italic", m.group(1)))
            elif m is m_link:
                tokens.append(("link", m.group(1)))  # текст ссылки; URL опускаем ради простоты
            i = m.end()

    tokenize(text, "text")
    for kind, chunk in tokens:
        run = paragraph.add_run(chunk)
        if kind in ("code", "bold_code"):
            run.font.name = "Courier New"
            run.font.size = Pt(10)
        if kind in ("bold", "bold_code"):
            run.bold = True
        if kind == "italic":
            run.italic = True


def _parse_alignments(separator_row: list[str]) -> list[str]:
    """`---` -> left, `---:` -> right, `:---:` -> center, `:---` -> left."""
    aligns = []
    for cell in separator_row:
        c = cell.strip()
        left = c.startswith(":")
        right = c.endswith(":")
        if left and right:
            aligns.append("center")
        elif right:
            aligns.append("right")
        else:
            aligns.append("left")
    return aligns


ALIGN_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
}


def _split_row(row: str) -> list[str]:
    # `| a | b |`  ->  ["a", "b"]
    parts = row.strip().split("|")
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _add_table(doc, rows: list[list[str]], aligns: list[str]):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid Accent 1"
    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            cell = table.rows[r_idx].cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = ALIGN_MAP[aligns[c_idx]]
            _add_inline(p, cell_text)
            if r_idx == 0:
                for run in p.runs:
                    run.bold = True
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    doc.add_paragraph()


def _add_code_block(doc, code_lines: list[str], _lang: str):
    para = doc.add_paragraph()
    run = para.add_run("\n".join(code_lines))
    run.font.name = "Courier New"
    run.font.size = Pt(9)


def _add_image(doc, md_path: Path, image_rel: str):
    img_path = (md_path.parent / image_rel).resolve()
    if not img_path.exists():
        doc.add_paragraph(f"[missing image: {image_rel}]")
        return
    doc.add_picture(str(img_path), width=Inches(6.0))
    last = doc.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER


def convert(md_path: Path, out_path: Path):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # fenced code block
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            _add_code_block(doc, buf, lang)
            i += 1  # skip closing ```
            continue

        # image on its own line
        m_img = IMAGE_RE.match(stripped)
        if m_img:
            _add_image(doc, md_path, m_img.group(1))
            i += 1
            continue

        # headings
        if stripped.startswith("### "):
            p = doc.add_paragraph()
            p.style = doc.styles["Heading 3"]
            _add_inline(p, stripped[4:])
            i += 1
            continue
        if stripped.startswith("## "):
            p = doc.add_paragraph()
            p.style = doc.styles["Heading 2"]
            _add_inline(p, stripped[3:])
            i += 1
            continue
        if stripped.startswith("# "):
            p = doc.add_paragraph()
            p.style = doc.styles["Title"]
            _add_inline(p, stripped[2:])
            i += 1
            continue

        # horizontal rule
        if stripped == "---":
            doc.add_paragraph().add_run("─" * 60)
            i += 1
            continue

        # GFM table: current line starts with `|`, next line is separator with `-`
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]):
            header = _split_row(lines[i])
            aligns = _parse_alignments(_split_row(lines[i + 1]))
            body_rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body_rows.append(_split_row(lines[j]))
                j += 1
            _add_table(doc, [header] + body_rows, aligns)
            i = j
            continue

        # bullet list block
        if stripped.startswith("- "):
            while i < len(lines) and lines[i].strip().startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                _add_inline(p, lines[i].strip()[2:])
                i += 1
            continue

        # numbered list block
        if re.match(r"^\d+\.\s", stripped):
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                p = doc.add_paragraph(style="List Number")
                _add_inline(p, re.sub(r"^\d+\.\s", "", lines[i].strip()))
                i += 1
            continue

        # paragraph: collect until blank line / structural line
        buf = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            nxt_s = nxt.strip()
            if not nxt_s:
                break
            if nxt_s.startswith(("#", "|", "```", "- ", "---")) or IMAGE_RE.match(nxt_s) or re.match(r"^\d+\.\s", nxt_s):
                break
            buf.append(nxt_s)
            i += 1
        p = doc.add_paragraph()
        _add_inline(p, " ".join(buf))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"Wrote {out_path}")


def _default_out(md_path: Path) -> Path:
    """week<N>/REPORT.md -> week<N>/Отчёт_Лабораторная_<N>_вариант5.docx.
    Иначе просто сменить расширение на .docx."""
    m = re.search(r"week(\d+)", str(md_path))
    if m:
        n = int(m.group(1))
        return md_path.parent / f"Отчёт_Лабораторная_{n}_вариант5.docx"
    return md_path.with_suffix(".docx")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md", type=Path, help="Путь к REPORT.md")
    parser.add_argument("--out", type=Path, default=None, help="Куда сохранить .docx")
    args = parser.parse_args()
    out = args.out or _default_out(args.md)
    convert(args.md, out)


if __name__ == "__main__":
    main()

# coding: utf-8
import io
import logging
import os
import re

LOG = logging.getLogger(__name__)


def convert_line_sep(content):
    # type: (str) -> str
    return content.replace("\u2028", "\n")


FLAGS = re.DOTALL | re.UNICODE | re.IGNORECASE

_sub_running_title1 = re.compile(r"\bLE\s+TYRAN\s+D'AXILANE\s+Michel\s+Grimaud\s+", flags=FLAGS).sub
_sub_running_title2 = re.compile(r"\bFolio\s+Junior\s+1998\s+", flags=FLAGS).sub


def convert_running_title(content):
    # "LE TYRAN D'AXILANE Michel Grimaud"
    # "Folio Junior 1998"
    content = _sub_running_title1("", content)
    content = _sub_running_title2("", content)
    return content


# "Illustration"
def del_illustration(mo):
    result = mo.group(1) + "\n"
    LOG.info("delete illustration: " + result.strip())
    return result


_sub_illustration = re.compile(r"\bIllustration\s+(\d+)\s+", flags=FLAGS).sub


def convert_illustration(content):
    return _sub_illustration(del_illustration, content)


def convert_sections(content):
    sections = ['<div>']
    for line in content.splitlines():
        sections.append(line)
        if "****" in line:
            sections.append('</div>')
            sections.append('<div>')
    while True:
        top = sections[-1]
        if top == '<div>':
            sections.pop()
            break
    return "\n".join(sections)


_sub_chapter = re.compile(r"(?<=\n)[IX|l\\/]+\s+Chapitre[ ]?\s+(.*?)\s*\n", flags=FLAGS).sub


class Chapters:
    def __init__(self):
        self.nos = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII']
        self.iter_nos = iter(self.nos)

    def format_title(self, mo):
        title = "Chapitre {no} – {title}".format(no=next(self.iter_nos), title=mo.group(1))
        LOG.info("format title: " + title)
        return "<h2>{title}</h2>\n".format(title=title)

    def __call__(self, content):
        content = content.replace("LE TYRAN D’AXILANE – Michel Grimaud",
                                  "<h1>LE TYRAN D’AXILANE – Michel Grimaud</h1>")
        return _sub_chapter(self.format_title, content)


convert_chapters = Chapters()

_sub_word_break = re.compile(r"(\w\w+)[~-]\s+(\w\w+)", flags=FLAGS).sub


def del_hyphen(mo):
    word = "".join(mo.groups())
    LOG.info("delete word break: " + word)
    return word


def convert_word_break(content):
    return _sub_word_break(del_hyphen, content)


_sub_folio = re.compile(r"(?:\b\d{1,3} \n|(?<=\n)\d{1,3}\n|\bl\d{1,2} \n|\b\d{1,2}l \n)", flags=FLAGS).sub


def del_folio(mo):
    LOG.info("delete folio: " + mo.group().strip())
    return u""


def convert_folio(content):
    return _sub_folio(del_folio, content)


def iter_paragraphs(content):
    # type: (str) -> str
    curr = ""
    for line in content.splitlines():
        line = line.rstrip()  # remove trailing whitespace
        if not curr:
            curr = line
        elif curr[-1] in ".?!*>":
            yield curr
            curr = line
        elif line.startswith("-"):
            yield curr
            curr = line
        else:
            curr += " " + line
    yield curr


def convert_paragraphs(content):
    return "\n".join(iter_paragraphs(content))


def convert_typo(content):
    content = re.sub(r"([.?!*>:])\s+[~-]\s?(\w)", r"\1\n- \2", content, flags=FLAGS)
    content = re.sub(r"\n-\s*(\w)", r"\n– \1", content, flags=FLAGS)
    content = re.sub(r"([.?!]\s+)ll\s+", r"\1Il ", content, flags=re.DOTALL | re.UNICODE)
    content = re.sub(r"\b([bcdfghijklmnpqrstvwxyz])[°'](\w+)", r"\1’\2", content, flags=FLAGS)
    content = re.sub(r"››", "»", content, flags=FLAGS)
    content = re.sub(r"(?:‹‹|``|`'|'`)", "«", content, flags=FLAGS)
    content = re.sub(r"\s*([?;:!%»])", "\u00a0" + r"\1", content, flags=re.DOTALL)
    content = re.sub(r"([«])\s*", r"\1" + "\u00a0", content, flags=re.DOTALL)
    content = re.sub(r"(\w)\.\.\.", r"\1…", content, flags=re.DOTALL)
    return content


HERE = os.path.dirname(__file__)


class SectionExporter:
    def __init__(self):
        self.docs_dir = os.path.join(os.path.dirname(HERE), "docs")
        assert os.path.isdir(self.docs_dir)
        self.rst_files = [
            "chapters/chap01-baladins.rst",
            "chapters/chap02-tikobal_barbe_or.rst",
            "chapters/chap03-rose_rouge.rst",
            "chapters/chap04-rose_blanche.rst",
            "chapters/chap05-paix.rst",
            "chapters/chap06-guerre.rst",
            "chapters/chap07-printemps_axilane.rst",
            "chapters/chap08-evasion_baladins.rst",
            "chapters/chap09-conquetes.rst",
            "chapters/chap10-fil_du_temps.rst",
        ]
        self.iter_rst = iter(self.rst_files)

    def format_h1(self, mo):
        title = mo.group(1)
        fmt = ("{line}\n"
               "{title}\n"
               "{line}")
        return fmt.format(title=title, line="=" * len(title))

    def format_h2(self, mo):
        title = mo.group(1)
        fmt = ("{title}\n"
               "{line}")
        return fmt.format(title=title, line="=" * len(title))

    def format_div(self, mo):
        text = mo.group(1)
        lines = []
        for line in text.splitlines():
            if not line and not line:
                continue
            line = re.sub(r"<h1>((?:(?!</h1>).)+)</h1>", self.format_h1, line, flags=FLAGS)
            line = re.sub(r"<h2>((?:(?!</h2>).)+)</h2>", self.format_h2, line, flags=FLAGS)
            line = line.replace("*", "★")
            line = line.replace("★★★★", ".. centered:: ★★★★")
            lines.append(line)
        text = "\n\n".join(lines)
        relpath = next(self.iter_rst)
        rst_path = os.path.join(self.docs_dir, relpath)
        with io.open(rst_path, mode="w", encoding="utf-8") as f:
            f.write(text)
        return text

    def __call__(self, content):
        content = re.sub(r"<div>((?:(?!</div>).)+)</div>", self.format_div, content, flags=FLAGS)
        return content


export_sections = SectionExporter()

CONVERTERS = [
    ('convert_line_sep', convert_line_sep),
    ('convert_running_title', convert_running_title),
    ('convert_illustration', convert_illustration),
    ('convert_sections', convert_sections),
    ('convert_chapters', convert_chapters),
    ('convert_folio', convert_folio),
    ('convert_word_break', convert_word_break),
    ('convert_paragraphs', convert_paragraphs),
    ('convert_typo', convert_typo),
    ('export_sections', export_sections),
]

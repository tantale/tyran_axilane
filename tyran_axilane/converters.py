# coding: utf-8
import logging
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


_sub_chapter = re.compile(r"(?<=\n)[IX|l\\/]+\s+Chapitre[ ]?\s+(.*?)\s*\n", flags=FLAGS).sub


class Chapters:
    def __init__(self):
        self.nos = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII']
        self.iter_nos = iter(self.nos)

    def reset(self):
        self.iter_nos = iter(self.nos)

    def format_title(self, mo):
        title = "Chapitre {no} – {title}".format(no=next(self.iter_nos), title=mo.group(1))
        LOG.info("format title: " + title)
        return "<h2>{title}</h2>\n".format(title=title)

    def __call__(self, content):
        return _sub_chapter(self.format_title, content)


convert_chapters = Chapters()

_sub_word_break = re.compile(r"(\w\w+)-\s+(\w\w+)", flags=FLAGS).sub


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


CONVERTERS = [
    ('convert_line_sep', convert_line_sep),
    ('convert_running_title', convert_running_title),
    ('convert_illustration', convert_illustration),
    ('convert_chapters', convert_chapters),
    ('convert_folio', convert_folio),
    ('convert_word_break', convert_word_break),
]

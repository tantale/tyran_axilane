# coding: utf-8
import collections
import io
import logging
import os
import re

import tyran_axilane.dictionary

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


def check_spelling(content):
    def iter_words(text_or_tags):
        for mo in re.finditer(r"<[^>]+>|\w+", text_or_tags, flags=FLAGS):
            text_or_tag = mo.group()
            if not text_or_tag.startswith('<'):
                yield text_or_tag.lower()

    word_count = collections.Counter(iter_words(content))
    for common in word_count.most_common(100):
        LOG.info("Word '{0}' appears {1} times.".format(*common))

    dictionary = tyran_axilane.dictionary.DICTIONARY
    dictionary.update({
        # new words
        "axilane": "Axilane",
        "sidonel": "Sidonel",
        'sídonel': "Sidonel",
        "bombok": "bombok",
        "tarano": "Tarano",
        "wanolo": "Wanolo",
        "djazilehs": "Djazilehs",
        "djazileh": "Djazileh",
        "xorgombir": "Xorgombir",
        "bambrille": "Bambrille",
        'bambrílle': 'Bambrille',
        "ibril": "Ibril",
        "ilouri": "Ilouri",
        "camperolle": "Camperolle",
        "sarak": "sarak",
        "saraks": "saraks",
        "tikobal": "Tikobal",
        "bétéko": "Bétéko",
        "betéko": "Bétéko",
        "béteko": "Bétéko",
        "beteko": "Bétéko",
        "thazor": "Thazor",
        "gorok": "Gorok",
        'balodon': 'balodon',
        'akir': 'Akir',

        # fixes
        "lbril": "Ibril",
        "llouri": "Ilouri",
        "pelísses": "pelisses",
        "entamérent": "entamèrent",
        'laísse': "laisse",
        'oublíez': "oubliez",
        'lajeta': 'la jeta',
        'roseraíe': 'roseraie',
        'éclaíra': 'éclaira',
        'lechamp': 'le-champ',
        'ecoute': 'écoute',

        'promít': 'promit',
        'etrange': 'étrange',
        'll': 'il',
        'tíkobal': 'Tikobal',
        '0r': 'or',
        'paíllasse': 'paillasse',
        'etait': 'était',
        'connaís': 'connais',
        'toiî': 'toit',

        'rondel': 'rondel',
        'evidemment': 'évidemment',
        'em': 'en',
        'ressentít': 'ressentit',
        'axiiane': 'Axilane',
        'fenétre': 'fenêtre',
        'ecoutez': 'écoutez',
        'lls': 'ils',
        'evasion': 'évasion',
        'luimême': 'lui-même',
        'èveilla': 'éveilla',
        'nasion': 'nasion',
        'divertís': 'divertis',
        'conquetes': 'conquêtes',
        'nasions': 'nasions',
        'etonné': 'étonné',
        'diune': 'd’urne',
        'têtel': 'tête\u00a0!',
        'entoisant': 'entoisant',
        'lnutile': 'inutile',
        'protondeurs': 'profondeurs',
        'excèdé': 'excédé',
        'moimême': 'moi-même',
        'ebahis': 'ébahis',
    })

    # not matched
    dictionary.update({k: k for k in [
        "bœufs", "bœuf", "bœufs", "bœuf", "œil", "cœur", "ô",
        "exclama",
        "écroulent",
        "esclaffa",
        "quelqu",
        "aimeraís",
        "affairèrent",
        "écroula",
        "empressèrent",
        "envola",
        'écria',
        'saufs',
        'carquois',
        'faix',
        'refarda',
        'flêche',
        'entoisa',
        'enquit',
        'aujourd',
        'puisqu',
        'manœuvrer',
        'aerostats',
        'envolèrent',
        'emparèrent',
        'songeusement',
        'arcbouté',
        'retrouvailles',
        'emparait',
        'grésillaient',
        'prétait',
        'évanouit',
        'enfuit',
        'préparatif',
        'insurgea',
        'qu',

        'iii',
        'iv',
        'v',
        'vi',
        'vii',
        'viii',
        'ix',
        'x',
    ]})

    for word in word_count:
        if word not in dictionary:
            LOG.error("Missing word '{0}'".format(word))

    def fix_error(mo):
        w = mo.group()
        key = w.lower()
        if key in dictionary:
            replace = dictionary[key]  # type: str
            if w.isupper():
                return replace.upper()
            elif w.istitle():
                return replace.title()
            else:
                return replace
        else:
            return w

    return re.sub(r"\w+", fix_error, content, flags=FLAGS)


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
    ('check_spelling', check_spelling),
    ('export_sections', export_sections),
]

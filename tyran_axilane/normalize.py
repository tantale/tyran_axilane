# coding: utf-8
from __future__ import print_function

import io
import re


def normalize(src_path, dst_path):
    with io.open(src_path, mode="r", encoding='utf-8') as f:
        content = f.read()

    # "LE TYRAN D'AXILANE Michel Grimaud"
    # "Folio Junior 1998"

    content = content.replace(u"LE TYRAN D'AXILANE Michel Grimaud\n", u"")
    content = content.replace(u"Folio Junior 1998\n", u"")

    # "I Chapitre "
    nos = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII']
    iter_nos = iter(nos)

    def sub_title(mo):
        title = u"<h2>Chapitre {no} – {title}</h2>\n".format(no=next(iter_nos), title=mo.group(2))
        print(title.strip())
        return title

    content = re.sub(r"^(.*)Chapitre[ ]?[\u2028\n](.*?)[ ]?[\u2028\n]", sub_title, content, flags=re.MULTILINE | re.UNICODE)

    # don- naient
    def sub_hyphen(mo):
        word = "".join(mo.groups())
        print(word)
        return word

    content = re.sub(r"(\w\w+)-[ \n\u2028](\w\w+)", sub_hyphen, content, flags=re.UNICODE)

    def sub_folio(mo):
        print(mo.group().strip())
        return u""

    content = re.sub(r"\u2028?\d\d+[ ]\n", sub_folio, content, flags=re.DOTALL | re.UNICODE)

    content = content.replace(u"\u2028", u"<br/>\n")

    with io.open(dst_path, mode="w", encoding="utf-8") as f:
        f.write(content)


if __name__ == '__main__':
    normalize("tyran_axilane.txt", "tyran_axilane.html")

# coding: utf-8
import io
import os


def normalize(string):
    u"""
    Normalize a string to ASCII: convert accents to non accented characters.

    .. note:: "oe" and "ae" letters are dropped.

    >>> normalize(u"Dès Noël où un zéphyr haï me vêt de glaçons würmiens je dîne d'exquis rôtis de bœuf au kir à l'aÿ d'âge mûr & cætera")
    b"Des Noel ou un zephyr hai me vet de glacons wurmiens je dine d'exquis rotis de boeuf au kir a l'ay d'age mur & caetera"

    :type string: str or unicode
    :param string: the string to normalize.

    :rtype: str
    :return: the normalized string.
    """
    import unicodedata
    string = string.replace("œ", "oe").replace("Œ", "OE")
    string = string.replace("æ", "ae").replace("Æ", "AE")
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')


def load_dictionary(path):
    # Les mots du dictionnaire sont indexé par taille de mot
    words = {}
    with io.open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            key = word.lower()
            words[key] = word
    return words


HERE = os.path.dirname(__file__)
DICTIONARY = load_dictionary(os.path.join(HERE, "liste.de.mots.francais-utf8.dic"))

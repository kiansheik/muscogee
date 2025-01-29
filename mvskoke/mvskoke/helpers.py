import unicodedata

GRADES = ["l", "h", "n", "f", None]
VOWELS = "a e ē i o u v".split(" ")
LONG_VOWELS = "a ē o".split(" ")
DIPHTHONGS = "i ue vo".split(" ")
SHORT_VOWELS = "e u v".split(" ")
SHORT_LONG_VOWELS = {"v": "a", "e": "ē", "u": "o"}
LONG_SHORT_VOWELS = {"a": "v", "ē": "e", "o": "u"}
SONORANTS = "l m n w y".split(" ")


# Implementing grading follow https://viva.pressbooks.pub/mvskokelanguagepatterns/chapter/grades/
def lgrade(stem):
    # find index of last vowel in stem by finding the first vowel from the end
    i, vowel = find_last_vowel(stem)
    if (len(stem[i + 1 :]) >= 2 and stem[i + 1] in SONORANTS) or (
        stem[i - 1 : i + 1] in DIPHTHONGS
    ):
        return stem
    # replace the vowel with its long counterpart if in the dict
    return stem[:i] + SHORT_LONG_VOWELS.get(vowel, vowel) + stem[i + 1 :]


def hgrade(stem):
    return apply_h_grade(stem)


def ngrade(stem):
    # first, lgrade the stem
    long_stem = lgrade(stem)
    i, vowel = find_last_vowel(long_stem)
    if len(long_stem) > 1 and long_stem[i - 1 : i + 1] in DIPHTHONGS:
        i -= 1
        vowel = long_stem[i]
    # add the diacritic ogonek to the vowel
    # Add the circumflex diacritic
    lengthened_vowel_with_circumflex = remove_accents(vowel) + "\u0328"

    # Normalize to form a single composed character (if applicable)
    normalized = unicodedata.normalize("NFC", lengthened_vowel_with_circumflex)
    return stem[:i] + normalized + stem[i + 1 :]


def fgrade(stem):
    # first, lgrade the stem
    long_stem = lgrade(stem)
    i, vowel = find_last_vowel(long_stem)
    if len(long_stem) > 1 and long_stem[i - 1 : i + 1] in DIPHTHONGS:
        i -= 1
        vowel = long_stem[i]
    # add the diacritic ^ to the vowel
    # Add the circumflex diacritic
    lengthened_vowel_with_circumflex = remove_accents(vowel) + "\u0302"

    # Normalize to form a single composed character (if applicable)
    normalized = unicodedata.normalize("NFC", lengthened_vowel_with_circumflex)
    return stem[:i] + normalized + stem[i + 1 :]


# find last vowel Returns the index of last vowel in stem and also the vowel itself in a tuple
def find_last_vowel(stem):
    for i in range(len(stem) - 1, -1, -1):
        if stem[i] in VOWELS:
            return i, stem[i]
    return None, None


def apply_h_grade(stem):
    # Helper function to shorten a vowel
    def shorten_vowel(vowel):
        return LONG_SHORT_VOWELS.get(vowel, vowel)

    # Rule 1: Handle stems ending in two different consonants or "kk"
    if len(stem) > 2 and (
        (stem[-1] not in VOWELS and stem[-2] not in VOWELS and stem[-1] != stem[-2])
        or stem[-2:] == "kk"
    ):
        return stem[:-1] + "i" + stem[-1:]

    # Rule 2: Simplify other double consonants and add `-iy`
    elif len(stem) > 1 and stem[-1] == stem[-2] and stem[-1] not in VOWELS:
        return stem[:-1] + "iy"

    # When the stem ends in awC, -i-
    elif len(stem) > 2 and stem[-3:-1] == "vo" and stem[-1] not in VOWELS:
        return stem[:-3] + "vwi" + stem[-1]

    # Rule 3: Insert `h` before the last consonant (default aspirating grade rule)
    elif len(stem) > 1 and stem[-1] not in VOWELS:
        if stem[-2] in LONG_VOWELS:
            return stem[:-2] + shorten_vowel(stem[-2]) + "h" + stem[-1]
        elif stem[-2] in ["v", "u"]:
            alt = SHORT_LONG_VOWELS.get(stem[-2])
            return stem[:-2] + alt + "h" + stem[-1]
        else:
            return stem[:-1] + "h" + stem[-1]
    return None


def clean_symbols(word):
    # keep only unicode alpha symbols and hiphens
    return "".join([c for c in word.split(",")[0] if c.isalpha() or c == "-"])


def remove_accents(input_str):
    return input_str
    """
    Remove accents from a given string.
    
    Args:
        input_str (str): The input string with possible accented characters.
    
    Returns:
        str: The input string with accents removed.
    """
    # Normalize the string to decompose accents and diacritics
    normalized_str = unicodedata.normalize("NFD", input_str)
    # Filter out combining characters (diacritics)
    accent_removed = "".join(
        char for char in normalized_str if unicodedata.category(char) != "Mn"
    )
    return accent_removed

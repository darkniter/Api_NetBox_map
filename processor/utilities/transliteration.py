from transliterate import translit


def transliteration(name):
    return translit(name, "ru", reversed=True)

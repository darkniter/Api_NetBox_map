from transliterate import get_available_language_codes, translit, slugify
from transliterate.base import TranslitLanguagePack, registry
from transliterate.contrib.languages.ru.translit_language_pack import RussianLanguagePack
from functools import lru_cache

registry.register(RussianLanguagePack)


class ExampleLanguagePack(TranslitLanguagePack):
    language_code = "example"
    language_name = "Example"
    mapping = {u"",
               u""}

    pre_processor_mapping = {
                        u'А': u'A',
                        u'Б': u'B',
                        u'В': u'V',
                        u'Г': u'G',
                        u'Д': u'D',
                        u'Е': u'E',
                        u'Ё': u'E',
                        u'Ж': u'Zh',
                        u'З': u'Z',
                        u'И': u'I',
                        u'Й': u'Y',
                        u'К': u'K',
                        u'Л': u'L',
                        u'М': u'M',
                        u'Н': u'N',
                        u'О': u'O',
                        u'П': u'P',
                        u'Р': u'R',
                        u'С': u'S',
                        u'Т': u'T',
                        u'У': u'U',
                        u'Ф': u'F',
                        u'Х': u'H',
                        u'Ц': u'Ts',
                        u'Ч': u'Ch',
                        u'Ш': u'Sh',
                        u'Щ': u'Sch',
                        u'Ъ': u'',
                        u'Ы': u'Y',
                        u'Ь': u'',
                        u'Э': u'E',
                        u'Ю': u'Yu',
                        u'Я': u'Ya',
                        u'а': u'a',
                        u'б': u'b',
                        u'в': u'v',
                        u'г': u'g',
                        u'д': u'd',
                        u'е': u'e',
                        u'ё': u'e',
                        u'ж': u'zh',
                        u'з': u'z',
                        u'и': u'i',
                        u'й': u'y',
                        u'к': u'k',
                        u'л': u'l',
                        u'м': u'm',
                        u'н': u'n',
                        u'о': u'o',
                        u'п': u'p',
                        u'р': u'r',
                        u'с': u's',
                        u'т': u't',
                        u'у': u'u',
                        u'ф': u'f',
                        u'х': u'h',
                        u'ц': u'ts',
                        u'ч': u'ch',
                        u'ш': u'sh',
                        u'щ': u'sch',
                        u'ъ': u'',
                        u'ы': u'y',
                        u'ь': u'',
                        u'э': u'e',
                        u'ю': u'yu',
                        u'я': u'ya',
                }


# registry.register(ExampleLanguagePack, force=True)


class Gost2006RuLangPack(TranslitLanguagePack):
    """Russian language pack like GOST R 52535.1-2006 for NetBox.
    """
    language_code = "ru-gost"
    language_name = "Russian like GOST R 52535.1-2006"
    mapping = (
        u"abvgdeeziiklmnoprstufhcyeABVGDEEZIIKLMNOPRSTUFHCYE",
        u"абвгдеёзийклмнопрстуфхцыэАБВГДЕЁЗИЙКЛМНОПРСТУФХЦЫЭ",
    )

    reversed_specific_mapping = (
        u"еЕёЁэЭиИйЙ",
        u"eEeEeEiIiI"
    )

    pre_processor_mapping = {
        u"zh": u"ж",
        # u"kh": u"х",
        # u"tc": u"ц",
        u"ch": u"ч",
        u"sh": u"ш",
        u"shch": u"щ",
        # u"iu": u"ю",
        # u"ia": u"я",
        u"yu": u"ю",
        u"ya": u"я",
        u"Zh": u"Ж",
        # u"Kh": u"Х",
        # u"Tc": u"Ц",
        u"Ch": u"Ч",
        u"Sh": u"Ш",
        u"Shch": u"Щ",
        # u"Iu": u"Ю",
        # u"Ia": u"Я",
        u"Yu": u"Ю",
        u"Ya": u"Я",
    }

    reversed_specific_pre_processor_mapping = {
        u"ъ": u"",
        u"ь": u"",
        u"Ъ": u"",
        u"Ь": u""
    }


registry.register(Gost2006RuLangPack, force=True)

LANG_PADDING = max([len(lang) for lang in get_available_language_codes()])


@lru_cache
def transliterate(text, lang='ru-gost', reversed=True):
    # trans = translit(text, 'example')
    trans = translit(text, lang, reversed)
    print(f"translit[{lang:{LANG_PADDING}}]: {text} => {trans}")

    if trans.isascii():
        return trans
    else:
        for i in trans:
            if not i.isascii():
                print(i, i.isascii())
        raise ValueError(f"Incorrect transliteration table for '{lang}' language")


if __name__ == "__main__":
    print("get_available_language_codes:", get_available_language_codes())

    text = '40 лет Октября, 1 Maya 34.2'
    test_text = 'Съешь ещё этих мягких французских булок, да выпей же чаю.'

    print(f"slugify: {text} => {slugify(text)}")
    # print(f"slugify:", " => ".join([test_text, slugify(test_text)]))

    result = [transliterate(test_text, lang) for lang in get_available_language_codes()]
    result = [transliterate(test_text.lower(), lang) for lang in get_available_language_codes()]
    result = [transliterate(test_text.upper(), lang) for lang in get_available_language_codes()]
    print()

    trans_list = [
        'Электродный',
        'Коммунистическая',
        'Текстильщиков',
        '40 лет Октября',
        'Егорьевская',
        'Дзержинского',
        'Барышникова',
        'Совхозная',
        'Строителей 1-й',
        'Юбилейный',
        'Красноармейский',
        'Центральный'
        ]

    result = [transliterate(addr, 'ru') for addr in trans_list]
    print(result)

    # result = [transliterate(addr, 'example', reversed=False) for addr in trans_list]
    # print()

    result = [transliterate(addr) for addr in trans_list]
    print()

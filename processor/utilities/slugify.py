import unicodedata
import re
from functools import wraps


def check_isascii(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0].isascii():
            return func(*args, **kwargs)
        else:
            raise ValueError("Value contain not ASCII symbols")
    return wrapper


@check_isascii
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)

    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

    value = re.sub(r'[^\w\s-]', '', value).strip().lower()

    return re.sub(r'[\s]+', '-', value)

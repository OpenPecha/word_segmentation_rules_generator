import re
from pathlib import Path

from botok import TSEK

from .Utility.regex_replacer import replace_with_regex


def remove_special_characters(file_string, is_gold_corpus=False):
    # Some signs(i.e ?,+,- ) are presented in human annotated training files which needs to be edited
    # There are two different kind of TSEK, and here proper tsek been replaced
    special_characters = {"?": " ", "+": "", "-": "", "༌": TSEK}
    if is_gold_corpus:
        special_characters = {"?": " ", "+": "", "༌": TSEK}

    modified_content = re.sub(
        "|".join(re.escape(key) for key in special_characters.keys()),
        lambda match: special_characters[match.group(0)],
        file_string,
    )
    modified_content = remove_extra_spaces(modified_content)
    return modified_content


def remove_extra_spaces(file_string):

    pattern = r"[ ]+"
    replacement = " "
    modified_string = replace_with_regex({pattern: replacement}, file_string.strip())
    return modified_string


def adjust_spaces_for_non_affix(file_string):
    """
    Sometimes there error in gold corpus i.e
    string: ད གེ འོ་ བཀྲ་ཤིས་ ཤོག།
    Expected: དགེ འོ་ བཀྲ་ཤིས་ ཤོག།
    *Note that in དགེ འོ་, space before འོ་ is not closed,because this is an affix
    """
    pattern = r"([^་།_]) ([^ར ས འི འམ འང འོ འིའོ འིའམ འིའང འོའམ འོའང ། _])"
    replacement = r"\1\2"
    modified_string = replace_with_regex({pattern: replacement}, file_string)
    return modified_string


def adjust_spaces_for_affix(file_string):
    """
    Somtimes there error in gold corpus i.e
    String: །འཁོར་བ འི་ འབྲོག་ ནི་ མི་ བཟད་པ-འི།
    Expected string: །འཁོར་བ-འི་ འབྲོག་ ནི་ མི་ བཟད་པ-འི།
    """
    pattern = r"((?![་།_༠༡༢༣༤༥༦༧༨༩])[\u0F00-\u0FFF]) (ར|ས|འི|འམ|འང|འོ|འིའོ|འིའམ|འིའང|འོའམ|འོའང)"
    replacement = r"\1-\2"
    modified_string = replace_with_regex({pattern: replacement}, file_string)

    return modified_string


def adjust_spaces_for_tibetan_numbers(file_string):
    patterns = {
        r"(?<=[༠༡༢༣༤༥༦༧༨༩])([ ]+)(?=[༠༡༢༣༤༥༦༧༨༩])": r"",  # གཏམ་༡ ༢  ༣བྱ་བ་ -> གཏམ་༡༢༣བྱ་བ་
        r"\s*([༠༡༢༣༤༥༦༧༨༩]+)\s*": r" \1 ",  # གཏམ་༡༢༣བྱ་བ་ -> གཏམ་ ༡༢༣ བྱ་བ་,
    }
    modified_content = replace_with_regex(patterns, file_string)
    return modified_content


def adjust_spaces_for_non_tibetan_character(file_string):
    patterns = {
        r"(?<=[^\u0F00-\u0FFF\s]) (?=[^\u0F00-\u0FFF\s])": r"",  # For non tibetan characters
        r"\s*([^\u0F00-\u0FFF\s_-]+)\s*": r" \1 ",
    }
    modified_content = replace_with_regex(patterns, file_string)
    return modified_content


def transform_gold_corpus_for_botok_word_tokenizer_pipeline(file_string):

    """
    input: string of a file before going under max match(botok)
    output/return: cleaned/preprocess string
    """

    modified_content = remove_special_characters(file_string)

    # Joining all the words, not leaving spaces unless its for SHAD
    patterns = {r"(?<=([^།])) (?=([^།]))": ""}

    modified_content = replace_with_regex(patterns, modified_content)
    return modified_content


def transform_gold_corpus_for_tagging(file_string):

    """
    input: string where words are separated with space by human annotators before going to tagger
    output/return: cleaned/preprocess string where words are still separated by space
    """
    modified_content = remove_special_characters(file_string, is_gold_corpus=True)

    patterns = {
        "།[ ]+༄": "།_༄",  # ཕྲེང་བ།  ༄༅༅།-> ཕྲེང་བ།_༄༅༅།
        "༅[ ]+།": "༅_།",
        "(?<=།) (?=།)": "_",  # ༄༅༅། ། ། །རྒྱ་གར་ སྐད་དུ། -> ༄༅༅།_།_།_།རྒྱ་གར་ སྐད་དུ།
        "[ ]+།": "_།",  # རྣམ་གྲོལ་ ཞིང༌ ། ། ->རྣམ་གྲོལ་ ཞིང་ _།_།,
        "།[ ]+": "།_",
        r"(?<![༅།_])([།_]+)": r" \1",  # སྐད་དུ།_རཱ་ -> སྐད་དུ །_རཱ་
        r"([།_]+)(?![༄།_])": r"\1 ",  # སྐད་དུ།_རཱ་ -> སྐད་དུ།_ རཱ་
    }
    modified_content = replace_with_regex(patterns, modified_content)
    gold_corpus_output = adjust_spaces_for_non_affix(modified_content)
    gold_corpus_output = adjust_spaces_for_tibetan_numbers(gold_corpus_output)
    gold_corpus_output = adjust_spaces_for_non_tibetan_character(gold_corpus_output)
    gold_corpus_output = adjust_spaces_for_affix(gold_corpus_output)

    return gold_corpus_output


if __name__ == "__main__":
    file_string = Path("../data/TIB_train.txt").read_text(encoding="utf-8")
    modified_string = transform_gold_corpus_for_botok_word_tokenizer_pipeline(
        file_string
    )
    print(modified_string)

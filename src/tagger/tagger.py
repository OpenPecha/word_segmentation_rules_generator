import sys
from pathlib import Path

from botok import TSEK

# Add the root directory of your project to sys.path
root_path = (
    Path(__file__).resolve().parents[2]
)  # Adjust the number of parents as needed
sys.path.append(str(root_path))

from src.compare_strings import compare_gold_corpus_and_tokenized_output  # noqa
from src.data_processor import remove_extra_spaces  # noqa
from src.Utility.get_syllables import get_syllables  # noqa


def split_list_with_TSEK(list_to_split):
    specific_character = TSEK
    split_list = []

    for element in list_to_split:
        if specific_character in element:
            insert_list = element.split(specific_character)
            split_list += insert_list
        else:
            split_list.append(element)
    split_list = list(filter(None, split_list))
    return split_list


# Building a tagged list for unmatched gold corpus syllables
def gold_corpus_tagger(gold_corpus_words, gold_index, gold_index_track):
    """
    Input: List of words of gold corpus
    Output: list of each syllable followed by the proper tag
    Eg:
    Input: ['ལ་', 'ལ་ལ་', 'ལ་', 'ལ་བ་'], gold_index=0, gold_index_track =3
    Output: ['ལ་', 'B', 'ལ་','B', 'ལ་', 'I', 'ལ་','B']

    B: means start of new word
    I: Continuation of the previous word
    X: New word but contains affix in gold corpus i.e ར|ས|འི|འམ|འང|འོ|འིའོ|འིའམ|འིའང|འོའམ|འོའང
    Y: Continuation of the previous word but contains affix
    """
    gold_corpus_unmatched_word_list = gold_corpus_words[gold_index:gold_index_track]
    gold_corpus_syls_tagged = []

    for gold_corpus_unmatched_word in gold_corpus_unmatched_word_list:

        gold_corpus_unmatched_syls = get_syllables(gold_corpus_unmatched_word)

        new_word = True
        for gold_corpus_unmatched_syl in gold_corpus_unmatched_syls:
            gold_corpus_syls_tagged.append(gold_corpus_unmatched_syl)
            if new_word:
                if "-" in gold_corpus_unmatched_syl:
                    gold_corpus_syls_tagged.append("X")
                else:
                    gold_corpus_syls_tagged.append("B")
                new_word = False
            else:
                if "-" in gold_corpus_unmatched_syl:
                    gold_corpus_syls_tagged.append("Y")
                else:
                    gold_corpus_syls_tagged.append("I")
    return gold_corpus_syls_tagged


def tagger(file_string):

    (
        equal_number_of_syls,
        gold_corpus_output,
        botok_output,
    ) = compare_gold_corpus_and_tokenized_output(file_string)

    if equal_number_of_syls is False:
        return "ValueError: Output of gold corpus and botok output does not match. Something wrong in language structure."  # noqa

    gold_corpus_output = remove_extra_spaces(gold_corpus_output)
    botok_output = remove_extra_spaces(botok_output)

    gold_corpus_words = gold_corpus_output.split()
    # Spliting on space and affixes, if max match has'nt done it
    # pattern = r"\s+|ར|ས|འི|འམ|འང|འོ|འིའོ|འིའམ|འིའང|འོའམ|འོའང"
    # botok_words = re.split(pattern, botok_output)
    botok_words = botok_output.split()
    botok_words_count = len(botok_words)
    gold_corpus_words_count = len(gold_corpus_words)

    gold_index = 0
    botok_index = 0
    tagged_content = ""
    while botok_index < botok_words_count and gold_index < gold_corpus_words_count:
        # Checking if the word is same, '_' is ignored because of possiblity of shads alignment
        condition1 = botok_words[botok_index].replace("_", "") == gold_corpus_words[
            gold_index
        ].replace("_", "")

        # If the word matches perfectly in output of both botok and gold corpus
        if condition1:
            tagged_content += botok_words[botok_index] + "/U "
            gold_index += 1
            botok_index += 1
            continue

        gold_index_track = gold_index
        botok_index_track = botok_index

        # Find the occurence of the next perfect word that matches in output of both botok and gold corpus
        while (botok_index_track < botok_words_count) and (
            gold_index_track < gold_corpus_words_count
        ):

            condition_1 = botok_words[botok_index_track].replace(
                "_", ""
            ) == gold_corpus_words[gold_index_track].replace("_", "")

            botok_unmatched_words = "".join(
                botok_words[botok_index : botok_index_track + 1]  # noqa
            )
            gold_corpus_unmatched_words = "".join(
                gold_corpus_words[gold_index : gold_index_track + 1]  # noqa
            )

            botok_unmatched_words = botok_unmatched_words.replace("_", "").replace(
                "-", ""
            )
            gold_corpus_unmatched_words = gold_corpus_unmatched_words.replace(
                "_", ""
            ).replace("-", "")

            if condition_1 and (
                len(botok_unmatched_words) == len(gold_corpus_unmatched_words)
            ):
                break

            botok_unmatched_syls = split_list_with_TSEK(
                botok_words[botok_index : botok_index_track + 1]  # noqa
            )
            gold_corpus_unmatched_syls = split_list_with_TSEK(
                gold_corpus_words[gold_index : gold_index_track + 1]  # noqa
            )

            if len(botok_unmatched_syls) > len(gold_corpus_unmatched_syls):
                gold_index_track += 1
            elif len(botok_unmatched_syls) < len(gold_corpus_unmatched_syls):
                botok_index_track += 1
            else:
                gold_index_track += 1
                botok_index_track += 1

        # Calling function to get a tagged list for unmatched gold corpus syllables
        gold_corpus_syls_tagged = gold_corpus_tagger(
            gold_corpus_words, gold_index, gold_index_track
        )

        # Building tagged list for unmatched max match words based on gold corpus syllables
        botok_unmatched_word_list = botok_words[botok_index:botok_index_track]

        gold_corpus_syls_tagged_index = 0
        for botok_unmatched_word in botok_unmatched_word_list:
            botok_unmatched_syls = get_syllables(botok_unmatched_word)
            botok_unmatched_syls_count = len(botok_unmatched_syls)
            botok_syls = ""
            botok_tags = ""

            botok_unmatched_syls_index = 0
            for i in range(
                gold_corpus_syls_tagged_index,
                (gold_corpus_syls_tagged_index + (2 * botok_unmatched_syls_count)),
                2,
            ):
                # botok_syls += gold_corpus_syls_tagged[i]
                botok_syls += botok_unmatched_syls[botok_unmatched_syls_index]
                botok_unmatched_syls_index += 1
                botok_tags += gold_corpus_syls_tagged[i + 1]

            tagged_content += botok_syls + "/" + botok_tags + " "
            gold_corpus_syls_tagged_index = gold_corpus_syls_tagged_index + (
                2 * botok_unmatched_syls_count
            )

        gold_index = gold_index_track
        botok_index = botok_index_track

    return tagged_content


if __name__ == "__main__":
    file_string = Path("../data/TIB_test.txt").read_text(encoding="utf-8")
    tagged_output = tagger(file_string)
    with open("../data/TIB_test_maxmatched_tagged.txt", "w", encoding="utf-8") as file:
        file.write(tagged_output)

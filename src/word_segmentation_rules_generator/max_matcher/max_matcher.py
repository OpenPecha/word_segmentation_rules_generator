import re

from botok import Text 

from ..preprocessing.preprocessor import file_2_botok, adjust_spaces


def SHADS_alignment(file_string):
    '''
     Adjusting the shads alginment of max_match output, (to match gold_corpus_2_tagger output)
    '''
    modified_string = file_string
    patterns = {
         '_།_།_':'།_།',
          '།_།_':'།_།',
          '_།_།':'།_།',
          " _།":' །_'
    }
    for pattern, replacement in patterns.items():
        modified_string = re.sub(pattern, replacement, modified_string)
    return modified_string

def botok_max_matcher(file_string):
    """
    input: string of a file before going under max match(botok)
    output/return: cleaned/preprocess string and word segmented
    """
    preprocessed_string = file_2_botok(file_string)
    t = Text(preprocessed_string)
    max_match_output = t.tokenize_words_raw_text
    max_match_output = adjust_spaces(max_match_output)
    #max_match_output = SHADS_alignment(max_match_output)
    return max_match_output


if __name__ == "__main__":
    pass
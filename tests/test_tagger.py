from src.word_segmentation_rules_generator.tagger.tagger import tagger


def test_tagger():
    assert (
        tagger(
            "༄༅། །རྒྱལ་པོ་ ལ་ གཏམ་ བྱ་བ་ རིན་པོ་ཆེ འི་ ཕྲེང་་་བ། ལ་ ལ་ལ་ ལ་ ལ་བ་ ཡོད། དཔལ། དགེའོ་ བཀྲ་ཤིས་ ཤོག།"
        )
        == "༄༅།_།/U རྒྱལ་པོ་/U ལ་/U གཏམ་/U བྱ་བ་/U རིན་པོ་ཆེ-འི་/U ཕྲེང་་་བ/U །_/U ལ་ལ་/BB ལ་ལ་/IB ལ་བ་/U ཡོད/U །_/U དཔལ/U །_/U དགེའོ་/U བཀྲ་ཤིས་ཤོག/BIB །/U "  # noqa
    )

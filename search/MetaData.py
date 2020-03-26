import os
dirname = os.path.dirname(__file__)


class Meta:
    collectionPath = os.path.join(dirname, 'Trump Speechs/')
    documentsGenName = "speech_"
    collectionSize = 56
    stopWordListPath = os.path.join(dirname, "Stopword-List.txt")
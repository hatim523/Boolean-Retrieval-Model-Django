import pickle
from nltk.stem import PorterStemmer

class PreProcessingDocuments():
    # Constructor takes path and size of collection along with general name of documents (in this case: speech_)
    # Also path of stopWords is provided as argument
    def __init__(self, collectionPath, documentsGenName, collectionSize, stopWordListPath, DictName=""):
        try:
            self.collectionPath = collectionPath
            self.collectionSize = collectionSize
            self.documentsGenName = documentsGenName
            self.stopWordPath = stopWordListPath

            self.DictName = DictName
            if DictName == "":
                self.DictName = "result_"

            # setting up inverted index and positional index names
            self.InvertedName = self.DictName + "invertedIndex.p"  # Extension .p for pickle file
            self.PositionalName = self.DictName + "positionalIndex.p"
            self.CollectionIndexName = self.DictName + "collectionIndex.p"

            self.CollectionIndexing = {}  # Used only for GUI purpose
            self.PositionIndex = {}
            self.InvertedIndex = {}
            self.stopWordList = []

            # List of numbers for determining boundary b/w word and numbers
            self.NumberList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

            # Building stopword list
            self.__ConstructStopWordList()
        except FileNotFoundError:
            print("Collection path or stop words path provided is not valid")

    # Builds stopwords list from the given stopword path (Helper Function)
    def __ConstructStopWordList(self):
        try:
            f = open(self.stopWordPath)
            stopWords = f.read()
        except:
            print("Stopword file not found.")
        else:
            print("Stopword file successfully loaded and read")
        word = ""
        for letter in stopWords:
            if letter == "\n":
                if word != "":
                    self.stopWordList += [word]
                word = ""
            else:
                word += letter

    # Processes each document one by one by calling various preprocessing functions
    def ProcessDocument(self):
        if self.CheckforStoredDictionary():
            return None

        for i in range(self.collectionSize):
            file_handler = open(self.collectionPath + self.documentsGenName + str(i) + ".txt")
            self.tokenizeDocument(file_handler.read(), i)
        self.BuildInvertedIndex()
        self.StoreDictionary()

    # Tokenizes the recieved document, including casefolding and removing stopwords
    def tokenizeDocument(self, documentData, documentNumber):
        document_name = "doc_" + str(documentNumber)

        # seperating words in document
        temp = ""
        i = 0
        for letter in documentData:
            # skip letters which are ", '
            if self.skipLetterFound(letter):
                continue

            if len(temp) > 0 and letter in self.NumberList and temp[
                -1] not in self.NumberList and PreProcessingDocuments.IgnoreWords(temp):
                # applying preprocessing steps to temp(token)
                self.AddtoCollectionIndex(temp, document_name, i)
                temp = PreProcessingDocuments.caseFold(temp)
                if not self.isStopWord(temp):
                    temp = PreProcessingDocuments.stemWord(temp)
                    # Adding the acquired word to Positional Index
                    self.AddtoIndex(temp, document_name, i)
                i += 1
                temp = letter
            elif PreProcessingDocuments.BreakingCharacterFound(letter):
                if not PreProcessingDocuments.IgnoreWords(temp):
                    self.AddtoCollectionIndex(temp, document_name, i)
                    processed_temp = PreProcessingDocuments.caseFold(temp)
                    # Skipping word if it is a stop word
                    if not self.isStopWord(processed_temp):
                        processed_temp = PreProcessingDocuments.stemWord(processed_temp)
                        # Now adding the acquired word from document into Positional Index
                        self.AddtoIndex(processed_temp, document_name, i)
                    i += 1
                temp = ""
            else:
                temp += letter

    # Adds or updates the dictionary based on the recieved token
    def AddtoIndex(self, token, document_name, token_position):
        if token not in self.PositionIndex:  # If token recieved is new
            self.PositionIndex[token] = {document_name: [token_position]}
        elif document_name in self.PositionIndex[token]:  # If token recieved and document_id are already in Index
            self.PositionIndex[token][document_name] += [token_position]
        else:  # If token is already in Index but not the document_id
            self.PositionIndex[token][document_name] = [token_position]

    def AddtoCollectionIndex(self, token, document_name, token_position):
        key = str(token_position) + "()" + document_name
        if key not in self.CollectionIndexing:   #If token recieved is new
            self.CollectionIndexing[key] = [token]
        else:
            self.CollectionIndexing[key] += [token]

    def BuildInvertedIndex(self):
        for key in self.PositionIndex.keys():
            self.InvertedIndex[key] = list(self.PositionIndex[key])

    def StoreDictionary(self):
        # saving positional index
        with open(self.PositionalName, 'wb') as fp:
            pickle.dump(self.PositionIndex, fp, protocol=pickle.HIGHEST_PROTOCOL)

        # saving inverted index
        with open(self.InvertedName, 'wb') as fp:
            pickle.dump(self.InvertedIndex, fp, protocol=pickle.HIGHEST_PROTOCOL)

        # saving collection inverted index
        with open(self.CollectionIndexName, 'wb') as fp:
            pickle.dump(self.CollectionIndexing, fp, protocol=pickle.HIGHEST_PROTOCOL)
        print("Dictionary saved")

    def CheckforStoredDictionary(self):
        try:
            print("Trying to Load stored dictionary")
            self.LoadDictionary()
            print("Dictionary successfully loaded!")
            return True
        except FileNotFoundError:
            print("No stored dictionary found...Building dictionary from scratch")
            return False

    def LoadDictionary(self):
        # Loading positional index
        with open(self.PositionalName, 'rb') as fp:
            self.PositionIndex = pickle.load(fp)

        # Loading inverted index
        with open(self.InvertedName, 'rb') as fp:
            self.InvertedIndex = pickle.load(fp)

        # Loading collection index
        with open(self.CollectionIndexName, 'rb') as fp:
            self.CollectionIndexing = pickle.load(fp)
    #############################################################################################################
                                # Functions used for creating and seperating tokens#
    #############################################################################################################

    # Returns true if the word is useless i.e contains a unicode character such as – or any other word
    # that doesn't qualify to be in english
    @staticmethod
    def IgnoreWords(word):
        if word == '–':
            return True
        elif word == "?":
            return True
        elif word == "!":
            return True
        elif word == "[":
            return True
        elif word == "]":
            return True
        elif word == "â…":
            return True
        elif word == "\"":
            return True
        elif word == "'":
            return True
        elif word == "":
            return True
        elif word == ".":
            return True
        elif word == " ":
            return True
        elif word == ",":
            return True

        return False

    # Returns true if any character that breaks a word is found
    @staticmethod
    def BreakingCharacterFound(letter):
        if letter == " ":
            return True
        elif letter == ":":
            return True
        elif letter == ".":
            return True
        elif letter == "[":
            return True
        elif letter == "]":
            return True
        elif letter == ",":
            return True
        elif letter == "?":
            return True
        elif letter == "!":
            return True
        elif letter == "\n":
            return True
        elif letter == "—":
            return True
        elif letter == "-":
            return True
        elif letter == "/":
            return True
        elif letter == "Â":
            return True
        elif letter == '(':
            return True
        elif letter == ')':
            return True
        elif letter == 'â':
            return True
        elif letter == '–':
            return True

        return False

    # Returns true if any skip letters such as ' or " is found
    def skipLetterFound(self, letter):
        if letter == "'":
            return True
        elif letter == "\"":
            return True
        elif letter == "€":
            return True
        elif letter == "”":
            return True

        return False

    # Converts the case of token to lowercase
    @staticmethod
    def caseFold(token):
        return token.lower()

    # Returns true if the word is a stop word
    def isStopWord(self, token):
        if token in self.stopWordList:
            return True
        return False

    # Stem the word using porter stemmer algorithm
    @staticmethod
    def stemWord(token):
        stemPorter = PorterStemmer()
        return stemPorter.stem(token)

    # Returns copy of the built Positional Index
    def GetPositionalIndex(self):
        return self.PositionIndex

    # Returns copy of the built Inverted Index
    def GetInvertedIndex(self):
        return self.InvertedIndex

    def GetCollectionIndex(self):
        return self.CollectionIndexing
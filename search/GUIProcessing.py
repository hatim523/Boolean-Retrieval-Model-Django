from nltk.stem import PorterStemmer

class GUIFunctions():

    @staticmethod
    def GetDocuments(queryResult):
        if type(queryResult) == list:
            return [i.strip('doc_') for i in queryResult]
        elif type(queryResult) == dict:
            return [i.strip('doc_') for i in list(queryResult.keys())]

    @staticmethod
    def GenerateLinesGivenDictionary(queryTerms, documents, collectionIndex, positionalIndex):
        doc_lines = {}

        for doc in documents.keys():
            line = []
            for i in range(documents[doc][0] - 5, documents[doc][0] + 9):
                line += [collectionIndex[str(i) + "()" + doc][0]]
            if doc in doc_lines.keys():
                doc_lines[int(doc.strip("doc_"))] += [line]
            else:
                doc_lines[int(doc.strip("doc_"))] = [line]

        return doc_lines

    @staticmethod
    def GenerateLines(queryTerms, documents, collectionIndex, positionalIndex, rawResults):
        doc_lines = {}
        print("Type: ", type(documents))
        if type(rawResults) == dict:
            print("Calling function generateLinesByDictionary")
            return GUIFunctions.GenerateLinesGivenDictionary(queryTerms, rawResults, collectionIndex, positionalIndex)

        # for doc in documents:
        #     line = []
        #     for term in queryTerms:
        #         print(term, " , ", "doc_" + doc)
        #         try:
        #             term_pos = positionalIndex[term]["doc_" + doc]
        #         except KeyError:
        #             continue
        #         for j in range(term_pos[0]-10, term_pos[0]+10):
        #             print(j, type(j))
        #             print(doc, type(doc))
        #             # print(collectionIndex[j][int(doc)]['doc_' + doc])
        #             try:
        #                 line.append(collectionIndex[str(j) + "()" + "doc_" + doc][0])
        #             except (IndexError, KeyError):
        #                 print("Index Error")
        #                 continue
        #             print(line)
        #         if doc in doc_lines.keys():
        #             doc_lines[int(doc)] += [[line]]
        #         else:
        #             doc_lines[int(doc)] = [[line]]

        for term in queryTerms:
            for doc in documents:
                line = []
                try:
                    term_index = positionalIndex[term]["doc_" + doc]
                except (KeyError, IndexError):
                    print("Term: ", term , " not found in document: ", doc)
                else:
                    for i in range(term_index[0] - 5, term_index[0] + 9):
                        if i < 0:
                            continue
                        line += [collectionIndex[str(i) + "()" + "doc_" + doc][0]]
                    if doc in doc_lines.keys():
                        doc_lines[doc] += [line]
                    else:
                        doc_lines[doc] = [line]

        if not bool(doc_lines): #if dictionary remains empty
            for i in documents:
                doc_lines[i] = ["None"]
        return doc_lines
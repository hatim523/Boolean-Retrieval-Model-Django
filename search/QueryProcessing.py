from .DocumentProcessing import PreProcessingDocuments


class ProcessQuery():
    def __init__(self, PositionalIndex, CollectionSize):
        self.keyWords = ['and', 'or', 'not', 'AND', 'OR', 'NOT']

        self.PositionalIndex = PositionalIndex
        self.CollectionSize = CollectionSize

        # Query recieved is stored here
        self.query = None

        # Query converted into token is stored here
        self.tokenizedQuery = []

        # Order to process query is saved here
        self.QueryQueue = []

        # List of numbers for determining the type of query
        self.NumberList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        #Type of query is stored here
        self.QueryType = None
    # Recieves query and determines the type of query namely: phrasal query, proximity query, or boolean query
    def QueryDocuments(self, query):
        print("Recieved Query: ", query)
        self.query = PreProcessingDocuments.caseFold(query) + " "
        self.tokenizedQuery = []

        self.__TokenizeQuery(self.query)
        #         print(self.tokenizedQuery)

        # determining the type of query
        if '(' in self.tokenizedQuery and ')' in self.tokenizedQuery:
            self.QueryType = "Complex Boolean Query"
            return self.__ComplexBooleanHandler()
        elif self.tokenizedQuery[-1] in self.NumberList:  # Done with proximity query
            self.QueryType = "Proximity Query"
            return self.__ProximityQueryHandler()
        elif len(self.tokenizedQuery) > 1 and not self.keyWordFound(self.tokenizedQuery):
            self.QueryType = "Phrasal Query"
            return self.__PhrasalQueryHandler()
        else:
            self.QueryType = "Simple Boolean Query"
            return self.__SimpleBooleanQueryHandler(self.tokenizedQuery)

    # Tokenizes the query into a list
    def __TokenizeQuery(self, query):
        token = ""

        for letter in query:
            if PreProcessingDocuments.BreakingCharacterFound(letter):
                if not PreProcessingDocuments.IgnoreWords(token):
                    token = PreProcessingDocuments.stemWord(token)
                    self.tokenizedQuery += [token]
                token = ""
            else:
                token += letter
            if letter == '(' or letter == ')':
                self.tokenizedQuery += [letter]
                temp = ""

    def getTerms(self):
        only_terms = []
        for term in self.tokenizedQuery:
            if term not in self.keyWords and term not in self.NumberList and term != '(' and term != ')':
                only_terms += [term]

        return only_terms

    def getQueryType(self):
        return self.QueryType

    #############################################################################################################
                                # FUNCTIONS FOR HANDLING DIFFERENT TYPES OF QUERIES#
    #############################################################################################################


    # Handles Proximity Query
    def __ProximityQueryHandler(self):
        print("Proximity")

        if len(self.tokenizedQuery) == 3:
            return self.Proximity(self.tokenizedQuery[0], self.tokenizedQuery[1], int(self.tokenizedQuery[2]))
        else:
            print("Condition not mentioned for catering longer proximity terms")
            return None

    # Handles Phrasal Query
    def __PhrasalQueryHandler(self):
        print("Phrasal")

        QueryCopy = self.tokenizedQuery.copy()
        term1 = QueryCopy.pop(0)
        result = self.Proximity(term1, QueryCopy.pop(0), 0)
        distance = 1
        while len(QueryCopy) > 0:
            term2 = QueryCopy.pop(0)
            result = self.ExtendedPhrasalQuery(result, term2, distance)
            distance += 1  # Since distance increases from the first word as the phrase gets long
        #             print("Type Recieved: ", type(result))

        return result

    # Handles Simple Boolean Queries
    def __SimpleBooleanQueryHandler(self, query):
        print("Simple Boolean")
        print("Recieved Query: ", query)
        self.QueryQueue = query.copy()
        result = []

        term1 = self.QueryQueue.pop(0)

        if len(self.QueryQueue) == 0:
            return list(self.PositionalIndex[term1])
        # Handling not case
        elif term1 == 'not':
            operation = 'not'
            term1 = self.QueryQueue.pop(0)
            result = self.Negate(term1)
        else:
            operation = self.QueryQueue.pop(0)
            term2 = self.QueryQueue.pop(0)
            if operation == 'and':
                result = self.Intersect(term1, term2)
            elif operation == 'or':
                result = self.Union(term1, term2)

        while len(self.QueryQueue) > 0:
            operation = self.QueryQueue.pop(0)
            term2 = self.QueryQueue.pop(0)

            # Checking if term2 is 'not' ; If term2 == 'not' then popping another term from queue
            if term2 == 'not':
                term2 = self.Negate(self.QueryQueue.pop(0))

            if operation == 'and':
                result = self.Intersect(result, term2)
            elif operation == 'or':
                result = self.Union(result, term2)

        return result

    def __ComplexBooleanHandler(self):
        print("Complex Boolean")

        query_copy = self.tokenizedQuery.copy()
        # Process the bracket first then process from left to right

        # Finding number of brackets
        num_brackets = self.tokenizedQuery.count('(')

        # Processing the terms under bracket first
        for bracket in range(num_brackets):
            store_res_position = query_copy.index('(')
            query_copy.pop(store_res_position)

            temp_queue = []
            while True:
                temp_var = query_copy.pop(store_res_position)
                if temp_var == ')':
                    break
                else:
                    temp_queue += [temp_var]

            query_copy.insert(store_res_position, self.__SimpleBooleanQueryHandler(temp_queue))

        #         print("Query after solving brackets: ", query_copy)
        result = self.__SimpleBooleanQueryHandler(query_copy)
        return result

    # Returns true if any of the given keywords is found in the query
    def keyWordFound(self, query):
        for keyword in self.keyWords:
            if keyword in query:
                return True

    # Returns posting list of a term
    def getPostingList(self, term):
        try:
            return self.PositionalIndex[term].keys()
        except:
            return []

    # Returns integer document id for comparision
    def getDocumentInt(self, documentID):
        return int(documentID.strip('doc_'))


    #############################################################################################################
                                    # START OF QUERY PROCESSING FUNCTIONS#
    #############################################################################################################


    ####################################################################################
    # Input Format: Term in form of list(doc_id) or token
    # Output Format: List --> ['doc_1', 'doc_4', 'doc_12', 'doc_20', 'doc_21', 'doc_22',]
    ####################################################################################
    def Intersect(self, term1, term2):
        if type(term1) == str:
            term1_posting = list(self.getPostingList(term1))
        elif type(term1) == list:
            term1_posting = term1
        else:
            print(type(term1), " not supported in this function")
            return None

        if type(term2) == str:
            term2_posting = list(self.getPostingList(term2))
        elif type(term2) == list:
            term2_posting = term2
        else:
            print(type(term2), " not supported in this function")
            return None

        posting_anded = []
        term1_counter = 0
        term2_counter = 0

        while term1_counter < len(term1_posting) and term2_counter < len(term2_posting):
            t1 = self.getDocumentInt(term1_posting[term1_counter])
            t2 = self.getDocumentInt(term2_posting[term2_counter])

            if t1 == t2:
                posting_anded += [t1]
                term1_counter += 1
                term2_counter += 1
            elif t1 < t2:
                term1_counter += 1
            else:
                term2_counter += 1

        posting_anded = ["doc_" + str(i) for i in posting_anded]
        return posting_anded  # Return value list = ['doc_1', 'doc_3'...]

    # Returns two terms or'ed result
    #######################################################################################
    # Input: term in form of list or string
    # Output: List ['doc_1', 'doc_4', 'doc_12', 'doc_20', 'doc_21', 'doc_22', 'doc_26']
    #######################################################################################
    def Union(self, term1, term2):
        if type(term1) == str:
            term1_posting = list(self.getPostingList(term1))
        elif type(term1) == list:
            term1_posting = term1
        else:
            print(type(term1), " not supported in this function")
            return None

        if type(term2) == str:
            term2_posting = list(self.getPostingList(term2))
        elif type(term2) == list:
            term2_posting = term2
        else:
            print(type(term2), " not supported in this function")
            return None

        posting_ored = []
        term1_counter = 0
        term2_counter = 0

        while term1_counter < len(term1_posting) or term2_counter < len(term2_posting):
            if term1_counter < len(term1_posting):
                t1 = self.getDocumentInt(term1_posting[term1_counter])
            else:
                t1 = self.CollectionSize + 100  # Renders this list useless if length has exceeded

            if term2_counter < len(term2_posting):
                t2 = self.getDocumentInt(term2_posting[term2_counter])
            else:
                t2 = self.CollectionSize + 100

            if t1 == t2:
                posting_ored += [t1]
                term1_counter += 1
                term2_counter += 1
            elif t1 < t2:
                posting_ored += [t1]
                term1_counter += 1
            else:
                posting_ored += [t2]
                term2_counter += 1

        posting_ored = ["doc_" + str(i) for i in posting_ored]
        return posting_ored

    # Returns not (term) posting list
    #########################################################################################
    # Input: Term in form of list or string
    # Output: List e.g. ['doc_1', 'doc_4', 'doc_12', 'doc_20', 'doc_21', 'doc_22', 'doc_26']
    #########################################################################################
    def Negate(self, term):
        if type(term) == str:
            term_posting = list(self.getPostingList(term))
        elif type(term) == list:
            term_posting = term
        else:
            print(type(term), " not supported in this function")
            return None
        i = 0

        # creating posting list of all documents
        result = ['doc_' + str(i) for i in range(self.CollectionSize)]

        while i < len(term_posting):
            result.remove(term_posting[i])
            i += 1

        return result

    # helper function for handling proximity query and phrasal query
    # Returns dictionary with keys containing doc_id and values containing its position
    def Proximity(self, term1, term2, max_distance):
        # Finding documents that contain both terms
        documents_containing_both_terms = self.Intersect(term1, term2)

        result = {}
        for document in documents_containing_both_terms:

            for appearances_first_term in self.PositionalIndex[term1][document]:  # Extracts position of first term
                if appearances_first_term + (max_distance + 1) in self.PositionalIndex[term2][document]:
                    if document not in result.keys():
                        result[document] = [appearances_first_term]
                    else:
                        result[document] += [appearances_first_term]

        return result

    # Returns dictionary with keys containing doc_id and values containing its position
    def ExtendedPhrasalQuery(self, term1, term2, dist):
        # Finding documents that intersect two terms
        docs_containing_both = self.Intersect(list(term1.keys()), term2)

        result = {}
        for document in docs_containing_both:

            for appearances_first_term in term1[document]:
                if appearances_first_term + (dist + 1) in self.PositionalIndex[term2][document]:
                    if document not in result.keys():
                        result[document] = [appearances_first_term]
                    else:
                        result[document] += [appearances_first_term]

        return result
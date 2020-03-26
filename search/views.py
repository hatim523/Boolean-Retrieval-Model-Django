from django.http import HttpResponse
from django.shortcuts import render
from .QueryProcessing import ProcessQuery
from .DocumentProcessing import PreProcessingDocuments
from .MetaData import Meta
from timeit import default_timer as timer
from .GUIProcessing import GUIFunctions
# Create your views here.

try:
    DocProcessing = PreProcessingDocuments(Meta.collectionPath, Meta.documentsGenName, Meta.collectionSize, Meta.stopWordListPath)
    DocProcessing.ProcessDocument()
    QueryProcess = ProcessQuery(DocProcessing.GetPositionalIndex(), Meta.collectionSize)
except:
    message = "Something went wrong...Please check the if the documents path and name are valid in MetaData.py"
else:
    message = "Basic Search Engine"
def index(request):


    return render(request, 'search/index.html', {'message' : message})

def result(request):
    start = timer()
    received_query = request.GET['search']
    queryResults = QueryProcess.QueryDocuments(received_query)
    content_docs = GUIFunctions.GenerateLines(QueryProcess.getTerms(), GUIFunctions.GetDocuments(queryResults), DocProcessing.GetCollectionIndex(), DocProcessing.GetPositionalIndex(), queryResults)
    end = timer()
    #Processing the sentence dictionary
    new_dict = {}
    for key, value in content_docs.items():
        # print(key)
        for line in value:
            if key in new_dict.keys():
                new_dict[key] += [" ".join(line)]
            else:
                new_dict[key] = [" ".join(line)]

    for key in new_dict.keys():
        print(key)
        for values in new_dict.values():
            print(values)

    context = {
        'query_type' : QueryProcess.QueryType,
        'num_results' : len(queryResults),
        'time_taken' : "{0:.3f}".format(round(end-start,3)) + " seconds",
        'query_text' : received_query,
        'documents' : GUIFunctions.GetDocuments(queryResults),
        'doc_lines' : new_dict
    }
    return render(request, 'search/result.html', context)
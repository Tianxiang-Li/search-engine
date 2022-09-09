# Search Engine
This is a search engine for TREC Benchmark Data to compare the effects of three relevance ranking models

## Design Document
Language: Python 3.8 

My code requires the users to run at the root directory of the project. Then, users can build the indexes by calling:

$ cd …/searchEngine

$ python ./implementation/build.py input-documents-directory index-type index-directory

Example:

$ cd c:/Users/TianxiangLi /Desktop/ searchEngine

$ python ./implementation/build.py ./BigSample stem ./indexes

The program will write the index file to the index directory with name [index-type].txt. Then, the user can start query processing. If the users are calling the static query processing, here is the format of the command-line call:

$ python ./implementation/query.py index-directory query-file-path retrieval-model index-type result-file-path

Example:

$ python ./implementation/query.py ./indexes ./queryfile.txt cosine single ./results/cosine-single

If the users are calling the dynamic query processing, here is the format of the command-line call:

$ python ./implementation/query_dynamic.py index-directory query-file-path result-file-path

Example:

$ python ./implementation/query.py ./indexes ./queryfile.txt ./results/dynamic

Both for static query processing and dynamic one, the programs will write the retrieved document list for the queries to the result directory and output the runtime of the program on the console. For static query processing, the comments in the results will indicate which retrieval model the program used. For dynamic query processing, the comments in the results will indicate the retrieval model and the indexes the program used.

Here are the basic designs:

Query parsing:

While parsing the queries, the program will read lines from the query file and extract the id and title for each query. If the query parsing is called by static query processing, the function will return a dictionary of query list with query ids as the keys and the corresponding parsed and tokenized titles as the values. If called by dynamic query processing, the values of the query list will be a complete string of the title for further processing according to different index types. The parsing and tokenizing of the titles apply the same functions as those in project 1 when the program processes the documents according to the type of index.

While processing the index files, the program will create an object of index, which contains the necessary variables and counts for the relevance ranking models. The initiator of the index will read in lines from the index files, extract the lexicon and posting lists, and gather the document frequency, document term frequency, total number of terms, total term frequency, document lengths, and term positions. 

Details in readme.pdf

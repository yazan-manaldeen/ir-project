import pandas as pd

docs = pd.read_csv("../resources/antique/antique_docs_clean.csv")
docs_index = {}


def build_docs_index():
    itr = 0
    for doc in docs.values:
        for word in str(doc[2]).split():
            if word not in docs_index:
                docs_index[word] = []
            docs_index[word].append(itr)
        itr = itr + 1


def get_query_relevant_docs(query):
    relevant_docs_idx = set()
    for word in query.split():
        if word in docs_index:
            for idx in docs_index[word]:
                relevant_docs_idx.add(idx)
    return relevant_docs_idx

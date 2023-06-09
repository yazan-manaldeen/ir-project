import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from quora_rest_api.quora_lemmatize_text import get_lemmatize_texts

queries = pd.read_csv("../resources/qoura/qoura_queries_clean.csv")
vectorizer = TfidfVectorizer(stop_words='english')
queries_index = {}


def build_queries_index():
    itr = 0
    for query in queries.values:
        for word in str(query[2]).split():
            if word not in queries_index:
                queries_index[word] = []
            queries_index[word].append(itr)
        itr = itr + 1


def get_suggestion_relevant_queries(query):
    relevant_queries_idx = set()
    for word in query.split():
        if word in queries_index:
            for idx in queries_index[word]:
                relevant_queries_idx.add(idx)
    return relevant_queries_idx


def get_suggestions(query):
    processed = get_lemmatize_texts([query])[0]
    related_docs_idx = get_suggestion_relevant_queries(processed)
    related_docs = list(related_docs_idx)
    vectorized_docs = vectorizer.fit_transform(queries['lemmatized_text'][related_docs])
    vectorized_query = vectorizer.transform([processed])
    similarity_scores = cosine_similarity(vectorized_query, vectorized_docs)
    results = list(enumerate(similarity_scores[0]))
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    results = []
    for i, score in sorted_results[:5]:
        results.append({
            'query_id': str(queries['query_id'][related_docs[i]]),
            'query_text': queries['text'][related_docs[i]]
        })
    return results

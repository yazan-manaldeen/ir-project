import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = pd.read_csv("../resources/qoura/qoura_docs_clean.csv")

vectorizer = TfidfVectorizer(stop_words='english')


def get_query_result(query, related_docs, page, page_size):
    start = page * page_size
    vectorized_docs = vectorizer.fit_transform(docs['lemmatized_text'][related_docs])
    vectorized_query = vectorizer.transform([query])
    similarity_scores = cosine_similarity(vectorized_query, vectorized_docs)
    results = list(enumerate(similarity_scores[0]))
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    search_results = sorted_results[start:start + page_size]
    results = []
    for i, score in search_results:
        results.append({
            'doc_id': str(docs['doc_id'][related_docs[i]]),
            'doc_text': docs['text'][related_docs[i]]
        })
    return results, len(sorted_results)

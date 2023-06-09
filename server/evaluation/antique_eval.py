import json

import datefinder
import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from spellchecker import SpellChecker

queries = pd.read_csv("../resources/antique/antique_queries_clean.csv")
docs = pd.read_csv("../resources/antique/antique_docs_clean.csv")
qrels = pd.read_csv("../resources/antique/antique_qrels.csv")

index = {}
itr = 0
for doc in docs.values:
    for word in str(doc[2]).split():
        if word not in index:
            index[word] = []
        index[word].append(itr)
    itr = itr + 1


def query_index(query):
    relevant_docs_idx = set()
    for word in query.split():
        if word in index:
            for idx in index[word]:
                relevant_docs_idx.add(idx)
    return relevant_docs_idx


vectorizer = TfidfVectorizer(stop_words='english')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
spell = SpellChecker()
translation_table = {
    48: " zero ",  # 0
    49: " one ",  # 1
    50: " two ",  # 2
    51: " three ",  # 3
    52: " four ",  # 4
    53: " five ",  # 5
    54: " six ",  # 6
    55: " seven ",  # 7
    56: " eight ",  # 8
    57: " nine ",  # 9
    33: ' ',  # !
    34: ' ',  # "
    35: ' ',  # #
    36: ' ',  # $
    37: ' ',  # %
    38: ' ',  # &
    39: ' ',  # '
    40: ' ',  # (
    41: ' ',  # )
    42: ' ',  # *
    43: ' ',  # +
    44: ' ',  # ,
    45: ' ',  # -
    46: ' ',  # .
    47: ' ',  # /
    58: ' ',  # :
    59: ' ',  # ;
    60: ' ',  # <
    61: ' ',  # =
    62: ' ',  # >
    63: ' ',  # ?
    64: ' ',  # @
    91: ' ',  # [
    92: ' ',  # \
    93: ' ',  # ]
    94: ' ',  # ^
    95: ' ',  # _
    96: ' ',  # `
    123: ' ',  # {
    124: ' ',  # |
    125: ' ',  # }
    126: ' ',  # ~
}
global_abbr = json.load(open("../resources/jsons/global-abbr.json"))


def pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatize_word(word):
    if word in stop_words: return ''
    if word in global_abbr: return global_abbr[word]
    correction = spell.correction(word)
    if correction: word = correction
    tokens = nltk.word_tokenize(word)
    pos_tagged = nltk.pos_tag(tokens)
    tag = pos_tagger(pos_tagged[0][1])
    if tag is None:
        return tokens[0]
    else:
        return lemmatizer.lemmatize(tokens[0], tag)


def get_lemmatize_texts(texts):
    texts = [" ".join([
        match.strftime("%Y-%m-%d")
        for match in datefinder.find_dates(text, strict=True)
    ]) + " " + " ".join([
        lemmatize_word(word)
        for word in str(text).lower().translate(translation_table).split()
        if word not in stop_words
    ]) for text in texts]
    return texts


def getQueryResult(query, results_num):
    processed = get_lemmatize_texts([query])[0]
    print("Processed Query : " + processed)
    related_docs_idx = query_index(processed)
    if len(related_docs_idx) == 0: return []
    related_docs = list(related_docs_idx)
    vectorized_docs = vectorizer.fit_transform(docs['lemmatized_text'][related_docs])
    vectorized_query = vectorizer.transform([processed])
    similarity_scores = cosine_similarity(vectorized_query, vectorized_docs)
    results = list(enumerate(similarity_scores[0]))
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    results = []
    for i, score in sorted_results[:results_num]:
        if score < 0.1: break
        results.append({
            'doc_id': docs['doc_id'][related_docs[i]],
            'doc_text': docs['text'][related_docs[i]]
        })
    return results


def convert_id_to_str(array):
    new_array = []
    for item in array:
        new_array.append(int(str(item).replace('_', '')))
    return new_array


def calculate_precision_at_10(relevant_docs, retrieved_docs):
    retrieved_docs_at_10 = retrieved_docs[:10]
    relevant_and_retrieved = set(relevant_docs).intersection(set(retrieved_docs_at_10))
    precision = len(relevant_and_retrieved) / 10
    return precision


def calculate_precision(relevant_docs, retrieved_docs):
    relevant_and_retrieved = set(relevant_docs).intersection(set(retrieved_docs))
    not_relevant_and_retrieved_count = len(retrieved_docs) - len(relevant_and_retrieved)
    divisor = (len(relevant_and_retrieved) + not_relevant_and_retrieved_count)
    if divisor == 0: return 0
    precision = len(relevant_and_retrieved) / divisor
    return precision


def calculate_recall(relevant_docs, retrieved_docs):
    relevant_and_retrieved = set(relevant_docs).intersection(set(retrieved_docs))
    divisor = len(relevant_docs)
    if divisor == 0: return 0
    recall = len(relevant_and_retrieved) / divisor
    return recall


def calculate_average_precision(relevant_docs, retrieved_docs):
    average_precision = 0.0
    num_correct = 0
    precision_at_rank = []
    for i, doc in enumerate(retrieved_docs):
        if doc in relevant_docs:
            num_correct += 1
            precision = num_correct / (i + 1)
            precision_at_rank.append(precision)
    if num_correct > 0:
        average_precision = sum(precision_at_rank) / len(relevant_docs)
    return average_precision


def calculate_rr(relevant_docs, retrieved_docs):
    for i, doc in enumerate(retrieved_docs):
        if doc in relevant_docs:
            return 1 / (i + 1)
    return 0


def calculate_eval():
    precision_at_10_list = []
    precision_list = []
    recall_list = []
    average_precision_list = []
    rr_list = []
    number_of_docs = len(docs)
    TP_sum = 0
    FP_sum = 0
    FN_sum = 0
    TN_sum = 0

    for query in queries.values:
        if not query[2]: continue
        query_docs_idx = [qrel[1] for qrel in qrels.values if qrel[0] == query[0]]
        results = getQueryResult(get_lemmatize_texts([query[2]])[0], len(query_docs_idx))
        results_docs_idx = [doc['doc_id'] for doc in results]

        query_docs_idx = convert_id_to_str(query_docs_idx)
        results_docs_idx = convert_id_to_str(results_docs_idx)

        TP = 0
        FP = 0
        FN = 0
        TN = 0
        for results_doc_idx in results_docs_idx:
            if results_doc_idx in query_docs_idx:
                TP += 1
            else:
                FP += 1
        FN += (len(query_docs_idx) - TP)
        TN += (number_of_docs - TP - FP - FN)

        TP_sum += TP
        FP_sum += FP
        FN_sum += FN
        TN_sum += TN

        precision_at_10 = calculate_precision_at_10(query_docs_idx, results_docs_idx)
        precision_at_10_list.append(precision_at_10)

        precision = calculate_precision(query_docs_idx, results_docs_idx)
        precision_list.append(precision)

        recall = calculate_recall(query_docs_idx, results_docs_idx)
        recall_list.append(recall)

        average_precision = calculate_average_precision(query_docs_idx, results_docs_idx)
        average_precision_list.append(average_precision)

        rr = calculate_rr(query_docs_idx, results_docs_idx)
        rr_list.append(rr)

    avg_precision_at_10 = sum(precision_at_10_list) / len(precision_at_10_list)
    avg_precision = sum(precision_list) / len(precision_list)
    avg_recall = sum(recall_list) / len(recall_list)
    avg_map = sum(average_precision_list) / len(average_precision_list)
    avg_mrr = sum(rr_list) / len(rr_list)

    print()
    print("Confusion Matrix: ")
    print(pd.DataFrame([[TP_sum, FP_sum], [FN_sum, TN_sum]], columns=['Related', 'Not Related'],
                       index=['Retrieved', 'Not Retrieved']))
    print()
    print(pd.DataFrame([
        str(int(avg_precision_at_10 * 100)) + '%',
        str(int(avg_precision * 100)) + '%',
        str(int(avg_recall * 100)) + '%',
        str(int(avg_map * 100)) + '%',
        str(int(avg_mrr * 100)) + '%'
    ], columns=['Rate'],
        index=['Precision@10', 'Precision', 'Recall', 'Mean Average Precision (MAP)', 'Mean Reciprocal Rank (MRR)']))


if __name__ == '__main__':
    calculate_eval()

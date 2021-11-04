from werkzeug.datastructures import FileStorage
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import pairwise_distances
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from joblib import Parallel, delayed
from functools import lru_cache
from models.user import User
from typing import Callable
from openTSNE import TSNE
from io import StringIO
import numpy as np
import string
import re


def batch_processing(fn: Callable, data: list, **kwargs) -> list:
    return Parallel(n_jobs=-1, backend="multiprocessing")(
        delayed(fn)(data=i, **kwargs) for i in data)


def pdf_to_string(file: FileStorage):
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()

    parser = PDFParser(file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

    return(output_string.getvalue())


def process_text(data: str, **kwargs) -> str:
    @lru_cache(maxsize=None)
    def strip_tags(text: str) -> str:
        p = re.compile(r'<.*?>')
        return p.sub('', text)

    @lru_cache(maxsize=None)
    def get_wordnet_pos(word: str):
        tag = pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    # Kwargs
    stop_words = kwargs.get("stop_words", [])
    deep = kwargs.get("deep", False)

    with open('./stopwords.txt', 'r') as f:
        stop_words_file = [line.strip() for line in f]

    punctuation = r"[{0}]".format(re.sub(r"[-']", "", string.punctuation))

    stop_words = [*set(stopwords.words("english"))
                  .union(stop_words)
                  .union(["'s", "'ll", "n't", "'d", "'ve", "'m", "'re", "'"])
                  .union(stop_words_file)]

    # Lowercase
    data = data.lower() if deep else data

    # Strip tags
    data = strip_tags(data)

    # Symbols
    data = re.sub(r'[^\x00-\xb7f\xc0-\xff]', r' ', data)

    # Links
    data = re.sub(r'https?:\/\/.*[\r\n]*', '', data)

    # line breaks
    data = re.sub('-\n', r'', data)

    # Punctuation
    data = re.sub(punctuation, " ", data) if deep else data

    # tokenization
    data = " ".join(word_tokenize(data)) if deep else data

    # Numeral ranges
    data = re.sub(r'\d+-\d+', "", data)

    # Numerics
    data = [
        re.sub(r"^\d+$", r"", i)
        for i in re.findall(r"\S+", data)
    ] if deep else re.findall(r"\S+", data)

    # Remove extra characteres
    data = [*filter(lambda x: len(x) > 2, data)]

    lemmatizer = WordNetLemmatizer()
    tokens = [
        lemmatizer.lemmatize(
            token, get_wordnet_pos(token)
        ) for token in data
        if not token in stop_words] if deep else data

    return " ".join(tokens).strip()


def term_frequency(data: str, **kwargs) -> dict:
    tf = {}
    for word in data.split(" "):
        tf[word] = (tf[word] + 1) if (word in tf) else 1

    return {k: v
            for k, v in sorted(tf.items(), key=lambda item: item[1], reverse=True)}


def similarity_graph(corpus: list) -> dict:
    graph = {
        "nodes":        [],
        "distance":     [],
        "neighborhood": []}

    graph["nodes"] = [{
        "id": doc.id,
        "name": doc.file_name
    } for doc in corpus]

    dist = pairwise_distances(
        [doc.embedding for doc in corpus],
        metric="euclidean",
        n_jobs=-1)

    dist_norm = MinMaxScaler([0.01, 1]).fit_transform(dist)

    for i in range(len(corpus)):
        indices = np.argsort(dist[i])
        for j in range(len(corpus)):
            if j < i:
                graph["distance"].append({
                    "source": corpus[i].id,
                    "target": corpus[j].id,
                    "value": float(dist_norm[i][j])})
            if j > 0:
                graph["neighborhood"].append({
                    "source": corpus[i].id,
                    "target": corpus[int(indices[j])].id,
                    "value": j})
    return graph


def l2_norm(data: list) -> np.array:
    data = np.array(data, dtype=float)
    dist = np.sqrt((data ** 2).sum(-1))[..., np.newaxis]
    return data / dist


def calculateSample(corpus_size: int) -> float:
    if corpus_size > 500:
        return 1e-5

    return 1 * (1.0 / (10 ** int(corpus_size/100)))


def t_SNE(corpus: list, perplexity: int = 30) -> list:
    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        metric="euclidean",
        n_jobs=-1
    ).fit(np.array([doc.embedding for doc in corpus]))
    return tsne.tolist()


def synonyms(word: str) -> list:
    word = word.replace("-", "_")
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
            synonyms.append(lm.name())
    return [*set(synonyms)]


def sankey_graph(user: User) -> dict:
    sessions = user.sessions

    graph = {
        "sessions": [],
        "nodes": [],
        "links": [],
        "index": {
            f"{doc.id}": [None for i in range(len(sessions))]
            for doc in user.corpus}}

    for i, session in enumerate(sessions):
        graph["sessions"].append({
            "id": session.id,
            "name": session.name,
            "clusters": [],
            "size": len(session.index)})
        for j in range(session.clusters["cluster_k"]):
            cluster_id = f"session{i}_cluster{j}"
            cluster_name = session.clusters["cluster_names"][j]
            docs = session.clusters["cluster_docs"][cluster_name]
            color = session.clusters["colors"][j]

            graph["nodes"].append({
                "id": cluster_id,
                "name": cluster_name,
                "color": color,
                "order": j,
                "session": session.id,
                "docs": docs})
            graph["sessions"][i]["clusters"].append(cluster_id)

            for doc in docs:
                if doc in graph["index"]:
                    graph["index"][doc][i] = color

            if i == (len(sessions) - 1):
                continue

            next_session = sessions[i+1]
            for k in range(next_session.clusters["cluster_k"]):
                next_cluster_name = next_session.clusters["cluster_names"][k]
                intersection = set(
                    session.clusters["cluster_docs"][cluster_name]
                ).intersection(
                    set(next_session.clusters["cluster_docs"]
                        [next_cluster_name])
                )
                if len(intersection) > 0:
                    graph["links"].append({
                        "id": f"link_{j}_{k}",
                        "source": cluster_id,
                        "target": f"session{i+1}_cluster{k}",
                        "value": len(intersection)})

    return graph


def synonyms(word: str) -> list:
    word = word.replace("-", "_")
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
            synonyms.append(lm.name())
    return [*set(synonyms)]

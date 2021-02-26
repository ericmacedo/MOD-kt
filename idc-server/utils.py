def pdf_to_string(file):
    from io import StringIO

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
    
def process_text(text:str) -> str:
    import string, re
    from nltk import download as NLTK_Downloader
    from nltk.corpus import stopwords

    NLTK_Downloader("stopwords", quiet=True)

    def strip_tags(text: str) -> str:
        p = re.compile(r'<.*?>')
        return p.sub('', text)

    punctuation = r"[{0}]".format(re.sub(r"[-]", "", string.punctuation))

    stop_words = stopwords.words("english")
    
    tokens = list(filter(lambda x: x != "", [                   # 7th extra whitespaces
        re.sub(r"^\d+$", r"", i) for i in re.findall(r"\S+",    # 6th numerics
            re.sub(punctuation, " ",                            # 5th Punctuation
                re.sub('-\n', r'',                              # 4th line breaks
                    re.sub(r'[^\x00-\xb7f\xc0-\xff]', r' ',     # 3th symbols 
                        strip_tags(                             # 2nd tags
                            text.lower()                        # 1st lowercase 
                        )
                    )
                )
            )
        )
    ]))

    tokens = [
        token
        for token in tokens
        if not token in stop_words]

    return " ".join(tokens).strip()

def get_userData(userId:str, newData:list=[]) -> list:
    from database.models import User

    user = User.objects.get(userId=userId)
    corpus = user.corpus_tolist()

    return {
        "userId": userId,
        "corpus": corpus,
        "newData": newData}

def term_frequency(text:str) -> dict:
    tf = {}
    for word in text.split(" "):
        tf[word] = (tf[word] + 1) if (word in tf) else 1
    return tf

def cosine_distance_graph(userId:str) -> dict:
    from sklearn.metrics import pairwise_distances
    from models import Corpus
    import json

    graph = {
        "nodes": [],
        "links": []}
    corpus = Corpus.get_items(userId=userId)

    graph["nodes"] = [{
        "id": doc["id"],
        "name": doc["file_name"]
    } for doc in corpus]

    cos_dist = pairwise_distances(
        [doc["embedding"] for doc in corpus],
        metric="cosine",
        n_jobs=-1)
    for i in range(len(corpus)):
        for j in range(i):
            graph["links"].append({
                "source": i,
                "target": j,
                "value": cos_dist[i][j]})

    with open(f"./users/{userId}/graph.json",
             "w", encoding="utf-8") as jsonFile:
        json.dump(graph, jsonFile)

    del corpus, cos_dist
    return graph

def encode_documents(docs:list, model:str=None) -> list:
    import os
    from sentence_transformers import SentenceTransformer

    model = model if model else "./pre-trained/allenai-specter"
    
    transformer = SentenceTransformer(os.path.abspath(model))
    embeddings = transformer.encode(docs).tolist()

    del transformer
    return embeddings

def l2_norm(data: list) -> list:
    import numpy as np

    dist = np.sqrt((data ** 2).sum(-1))[...,np.newaxis]
    return list(data / dist)

def t_SNE(userId:str, perplexity:int=30) -> list:
    from openTSNE import TSNE
    from models import Corpus
    import numpy as np
    
    corpus = Corpus.get_items(userId=userId)

    import pdb; pdb.set_trace()

    tsne = TSNE(
        n_components = 2,
        perplexity=perplexity,
        metric="cosine",
        n_jobs=-1
    ).fit(np.array([doc["embedding"] for doc in corpus]))
    np.save(f"./users/{userId}/tsne.npy", tsne)
    tsne_embedding = tsne.tolist()

    del corpus, tsne
    return tsne_embedding

def UMAP(userId:str,
        n_neighbors:int=5,
        min_dist:int=0.1) -> list:
    from umap import UMAP
    from models import Corpus
    import numpy as np
    
    corpus = Corpus.get_items(userId=userId)

    umap = UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric="cosine",
        n_jobs=-1
    ).fit_transform([doc["embedding"] for doc in corpus])
    np.save(f"./users/{userId}/umap.npy", umap)
    umap_embedding = umap.tolist()

    del corpus, umap
    return umap_embedding

def Word2Vec(userId:str, data:list=None) -> dict:
    from models import Corpus
    from gensim.models import Word2Vec
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle
    import os

    model_path = f"./users/{userId}/Word2Vec.model"

    def calculateSample(corpus_size:int) -> float:
        if corpus_size > 500:
            return 1e-5
        return float(1 * (1.0/ (10 ** int(corpus_size/100))))
    
    corpus = Corpus.get_items(userId=userId)
    sentences = [
        doc["content"]
        for doc in (data if data else corpus)]
    corpus_size = len(corpus) + (len(data) if data else 0)

    model = Word2Vec.load(model_path) if (
        data and os.path.isfile(model_path)
    ) else (
        Word2Vec(
            min_count=5,
            window=8,
            size=100,
            alpha=0.025,
            min_alpha=0.0007,
            sample=calculateSample(corpus_size),
            hs=1,
            sg=1,
            negative=15,
            ns_exponent=0.75,
            workers=cpu_count(),
            iter=40))

    model.build_vocab(
        sentences=sentences,
        update=(True if data else False))
    
    oldVocab = set(model.wv.index2word) if data else None

    model.train(
        shuffle(sentences),
        total_examples=model.corpus_count, 
        epochs=40)
        
    newVocab = set(model.wv.index2word) if data else None
    newWords = newVocab.difference(oldVocab) if data else None
    indexes = [
        index for index, word in enumerate(newVocab)
        if word in newWords
    ] if data else None
    newData = [
        model.wv.vectors_norm[i]
        for i in indexes
    ] if data else None
    
    model.save(model_path)

    del ( 
        corpus, sentences, oldVocab,
        newVocab, newWords, indexes)
    return model
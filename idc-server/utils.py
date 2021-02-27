from database.models import User, EmbDocument
from werkzeug.datastructures import FileStorage

from nltk import download as NLTK_Downloader
NLTK_Downloader("stopwords", quiet=True)


def pdf_to_string(file:FileStorage):
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
    from nltk.corpus import stopwords

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

def cosine_distance_graph(corpus:list) -> dict:
    from sklearn.metrics import pairwise_distances

    graph = {
        "nodes": [],
        "links": []}

    graph["nodes"] = [{
        "id": doc.id,
        "name": doc.file_name
    } for doc in corpus]

    cos_dist = pairwise_distances(
        [doc.embedding for doc in corpus],
        metric="cosine",
        n_jobs=-1)

    for i in range(len(corpus)):
        for j in range(i):
            graph["links"].append({
                "source": i,
                "target": j,
                "value": cos_dist[i][j]})
    return graph

def encode_document(docs:str, model:str=None) -> list:
    import os
    from sentence_transformers import SentenceTransformer

    model = model if model else (
        os.path.abspath("./pre-trained/allenai-specter"))
    
    transformer = SentenceTransformer(model)
    embeddings = transformer.encode(docs).tolist()

    del transformer
    return embeddings

def l2_norm(data: list) -> list:
    import numpy as np

    dist = np.sqrt((data ** 2).sum(-1))[...,np.newaxis]
    return list(data / dist)

def t_SNE(corpus:list, perplexity:int=30) -> list:
    from openTSNE import TSNE
    import numpy as np

    tsne = TSNE(
        n_components = 2,
        perplexity=perplexity,
        metric="cosine",
        n_jobs=-1
    ).fit(np.array([doc.embedding for doc in corpus]))
    return tsne.tolist()

def UMAP(corpus:list,
        n_neighbors:int=5,
        min_dist:int=0.1) -> list:
    from umap import UMAP
    import numpy as np

    umap = UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric="cosine",
        n_jobs=-1
    ).fit_transform([doc.embedding for doc in corpus])
    return umap.tolist()

def calculateSample(corpus_size:int) -> float:
    if corpus_size > 500:
        return 1e-5
    
    return 1 * (1.0/ (10 ** int(corpus_size/100)))

def Word2Vec(user:User) -> dict:
    from gensim.models import Word2Vec
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle

    sentences = [
        doc.processed.split(" ")
        for doc in user.corpus]

    corpus_size = len(user.corpus)

    model = Word2Vec(
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
        iter=40)

    model.build_vocab(sentences=sentences)
    

    model.train(
        shuffle(sentences),
        total_examples=model.corpus_count, 
        epochs=40)

    model.wv.init_sims()
    return model.wv.vectors_norm

def Doc2Vec(user:User):
    from gensim.models.doc2vec import Doc2Vec, TaggedDocument
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle
    from tempfile import NamedTemporaryFile
    from bson.binary import Binary

    tagged_data = [
        TaggedDocument(
            doc.processed.split(" "),
            tags=[doc.id]
        ) for doc in user.corpus]

    corpus_size = len(tagged_data)

    model = Doc2Vec(
        dm=1,
        dm_mean=1,
        dbow_words=1,
        dm_concat=0,
        vector_size=100,
        window=8,
        alpha=0.025,
        min_alpha=0.0007,
        hs=0,
        sample=calculateSample(corpus_size),
        negative=15,
        ns_expoent=0.75,
        min_count=5,
        workers=cpu_count(),
        epochs=40)

    model.build_vocab(documents=tagged_data)

    model.train(
        documents=shuffle(tagged_data),
        total_examples=model.corpus_count,
        epochs=40)

    model.docvecs.init_sims()
    return model.docvecs.vectors_docs_norm
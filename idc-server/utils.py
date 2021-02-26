from database.models import User, EmbDocument
from werkzeug.datastructures import FileStorage

from nltk import download as NLTK_Downloader
NLTK_Downloader("stopwords", quiet=True,)


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

def cosine_distance_graph(corpus:list[EmbDocument]) -> dict:
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

def t_SNE(corpus:list[EmbDocument], perplexity:int=30) -> list:
    from openTSNE import TSNE
    import numpy as np

    tsne = TSNE(
        n_components = 2,
        perplexity=perplexity,
        metric="cosine",
        n_jobs=-1
    ).fit(np.array([doc.embedding for doc in corpus]))
    return tsne.tolist()

def UMAP(corpus:list[EmbDocument],
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

def Word2Vec(user:User, data:list=None) -> dict:
    from gensim.models import Word2Vec
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle
    from tempfile import NamedTemporaryFile
    import os

    def calculateSample(corpus_size:int) -> float:
        if corpus_size > 500:
            return 1e-5
        return float(1 * (1.0/ (10 ** int(corpus_size/100))))

    update = (data and user.word2vec)

    sentences = [
        doc.processed
        for doc in (data if data else user.corpus)]

    corpus_size = len(user.corpus) + (len(data) if data else 0)

    if update:
        # Create a temporary file and write the bytes into it
        # Gensim only supports file paths
        w_file = NamedTemporaryFile(mode="wb", suffix=".bin", delete=True)
        w_file.write(user.word2vec)
        model = Word2Vec.load(w_file.name)
        w_file.close()
    else:
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

    model.build_vocab(
        sentences=sentences,
        update=(True if update else False))
    
    oldVocab = set(model.wv.index2word) if update else None

    model.train(
        shuffle(sentences),
        total_examples=model.corpus_count, 
        epochs=40)
        
    newVocab = set(model.wv.index2word) if update else None
    newWords = newVocab.difference(oldVocab) if update else None
    indexes = [
        index for index, word in enumerate(newVocab)
        if word in newWords
    ] if update else None
    newData = [
        model.wv.vectors_norm[i]
        for i in indexes
    ] if update else None
    
    # Create a temporary file and write the W2V model into it
    w_file = NamedTemporaryFile(mode="wb", suffix=".bin", delete=True)
    model.save(w_file.name)
    f_name = w_file.name
    # Reads the temporary file and save the bytes into f_bytes
    r_file = open(f_name, mode="rb")
    f_bytes = r_file.read()
    w_file.close()
    r_file.close()

    user.update(word2vec=f_bytes)

    del (
        sentences, oldVocab, newVocab,
        newWords, indexes, f_bytes, f_name)
    return model

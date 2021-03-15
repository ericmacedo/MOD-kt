from models import User, Document
from werkzeug.datastructures import FileStorage
from gensim.models.doc2vec import Doc2Vec
from gensim.models import FastText, Word2Vec
from spacy.tokens.doc import Doc
from spacy import displacy


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
    
def process_text(text:str, deep:bool=False) -> str:
    import string, re
    from nltk.corpus import stopwords

    def strip_tags(text: str) -> str:
        p = re.compile(r'<.*?>')
        return p.sub('', text)

    punctuation = r"[{0}]".format(re.sub(r"[-]", "", string.punctuation))

    stop_words = stopwords.words("english")

    # 1st lowercase
    text = text.lower() if deep else text
    
    # strip tags
    text = strip_tags(text)
    
    # 3th symbols 
    text = re.sub(r'[^\x00-\xb7f\xc0-\xff]', r' ', text)

    # 4th line breaks
    text = re.sub('-\n', r'', text)
    
    # 5th Punctuation
    text = re.sub(punctuation, " ", text) if deep else text

    # 6th numerics
    tokens = [
        re.sub(r"^\d+$", r"", i)
        for i in re.findall(r"\S+", text)
    ] if deep else re.findall(r"\S+", text)

    # 7th extra whitespaces
    tokens = [*filter(lambda x: x != "", tokens)]

    tokens = [
        token
        for token in tokens
        if not token in stop_words] if deep else tokens

    return " ".join(tokens).strip()

def term_frequency(text:str) -> dict:
    tf = {}
    for word in text.split(" "):
        tf[word] = (tf[word] + 1) if (word in tf) else 1

    return { k: v
        for k, v in sorted(tf.items(), key=lambda item: item[1], reverse=True)}

def similarity_graph(corpus:list) -> dict:
    import numpy as np
    from sklearn.metrics import pairwise_distances
    from sklearn.preprocessing import MinMaxScaler

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

    dist_norm = MinMaxScaler([1e-5, 1]).fit_transform(dist)

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

def encode_document(docs:str, model:str=None) -> list:
    import os
    from sentence_transformers import SentenceTransformer

    model = model if model else (
        os.path.abspath("./pre-trained/allenai-specter"))
    
    transformer = SentenceTransformer(model)
    embeddings = transformer.encode(docs).tolist()

    del transformer
    return embeddings.tolist()

def l2_norm(data: list):
    import numpy as np

    dist = np.sqrt((data ** 2).sum(-1))[...,np.newaxis]
    return data / dist

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

def calculateSample(corpus_size:int) -> float:
    if corpus_size > 500:
        return 1e-5
    
    return 1 * (1.0/ (10 ** int(corpus_size/100)))

def Word_2_Vec(user:User) -> Word2Vec:
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
    return model

def Fast_Text(user:User) -> FastText:
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle

    sentences = [
        doc.processed.split(" ")
        for doc in user.corpus]

    corpus_size = len(user.corpus)

    model = FastText(
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
    return model

def Doc_2_Vec(user:User) -> Doc2Vec:
    from gensim.models.doc2vec import Doc2Vec, TaggedDocument
    from multiprocessing import cpu_count
    from sklearn.utils import shuffle
    from tempfile import NamedTemporaryFile

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
    return model

def displaCy_NER(doc: Doc) -> str:
    return displacy.render(
        docs=doc,
        style="ent",
        minify=True,
        page=False,
        jupyter=False)

def most_similar(user:User, positive:list, topn:int=10) -> list:
    model = user.fast_text if user.word_model == "FastText" else user.word2vec

    sim_wors = model.wv.most_similar(positive=positive, topn=topn)

    return [
        {"word": word[0], "value": word[1]}
        for word in sim_wors]
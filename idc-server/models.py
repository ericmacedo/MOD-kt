import os, json
import numpy as np
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec
from datetime import datetime
from uuid import uuid4

class User:
    def __init__(self, userId:str):
        self.userId = userId

        # PATHS
        self.__user     = f"./users/{self.userId}"
        self.__corpus   = f"{self.__user}/corpus"
        self.__sessions = f"{self.__user}/sessions"
        self.__graph    = f"{self.__user}/graph.json"
        self.__index    = f"{self.__user}/corpus.index"
        self.__tsne     = f"{self.__user}/tsne.npy"
        self.__umap     = f"{self.__user}/umap.npy"
        self.__word2vec = f"{self.__user}/Word2Vec.bin"
        self.__doc2vec  = f"{self.__user}/Doc2Vec.bin"

        if not os.path.isdir(self.__user):
            return None

    # INDEX
    @property
    def index(self) -> list:
        if os.path.isfile(self.__index):
            index = np.loadtxt(
                self.__index,
                encoding="utf-8",
                dtype=str).tolist()
            return [index] if type(index) == str else index
        return self.generate_index()

    def generate_index(self) -> list:
        ids = []
        for file in os.listdir(self.__corpus):
            id, ext = os.path.splitext(file)
            if ext == ".json":
                ids.append(id)
        
        np.savetxt(self.__index,
            ids,
            encoding="utf-8",
            fmt="%s",
            newline="\n")
        return ids

    # CORPUS
    @property
    def corpus(self) -> list:
        return [Document(
            userId=self.userId, id=id
        ) for id in self.index]

    def append_document(self,
                        file_name:str,
                        content:str,
                        term_frequency:dict,
                        processed:str,
                        embedding:list=None):

        uuid = str(uuid4())
        file_path = f"{self.__corpus}/{uuid}.json"

        document = {
            "id": uuid,
            "file_name": file_name,
            "content": content,
            "processed": processed,
            "term_frequency": term_frequency,
            "uploaded_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC")}
        if embedding:
            document["embedding"] = embedding

        with open(file_path, "w", encoding="utf-8") as out_file:
            json.dump(document, out_file)
        
        with open(self.__index, "a") as index_file:
            index_file.write(f"{uuid}\n")

    def delete_documents(self, ids:list):
        for f_path in os.listdir(self.__corpus):
            id, ext = os.path.splitext(f_path)
            if ext == ".json" and id in ids:
                os.remove(f"{self.__corpus}/{f_path}")
        self.generate_index()

    # SESSIONS
    @property
    def sessions(self):
        sessions = []
        for file in os.listdir(self.__sessions):
            id, ext = os.path.splitext(file)
            if ext == ".json":
                sessions.append(Session(
                    userId=self.userId,
                    id=id))
        return sessions
    
    def append_session(self, session:dict):
        #TODO
        pass
    
    def delete_sessions(self, ids:list):
        for f_path in os.listdir(self.__sessions):
            id, ext = os.path.splitext(f_path)
            if ext == ".json" and id in ids:
                os.remove(f"{self.__sessions}/{f_path}")

    # GRAPH
    @property
    def graph(self) -> dict:
        graph = None
        if os.path.isfile(self.__graph):
            with open(self.__graph, "r", encoding="utf-8") as f_graph:
                graph = json.load(f_graph)
        return graph
    
    @graph.setter
    def graph(self, graph:dict):
        with open(self.__graph, "w", encoding="utf-8") as g_file:
            json.dump(graph, g_file)

    # TSNE
    @property
    def tsne(self) -> list:
        if os.path.isfile(self.__tsne):
            return np.load(self.__tsne).tolist()
        return None

    @tsne.setter
    def tsne(self, tsne):
        np.save(self.__tsne, np.array(tsne, dtype=np.float64))

    # UMAP
    @property
    def umap(self) -> list:
        if os.path.isfile(self.__umap):
            return np.load(self.__umap).tolist()
        return None

    @umap.setter
    def umap(self, umap):
        np.save(self.__umap, np.array(umap, dtype=np.float64))

    # WORD2VEC
    @property
    def word2vec(self) -> Word2Vec:
        if os.path.isfile(self.__word2vec):
            model = Word2Vec.load(self.__word2vec)
            model.wv.init_sims()
            return model
        return None

    @word2vec.setter
    def word2vec(self, word2vec:Word2Vec):
        word2vec.save(self.__word2vec)

    # DOC2VEC
    @property
    def doc2vec(self) -> Doc2Vec:
        if os.path.isfile(self.__doc2vec):
            model = Word2Vec.load(self.__doc2vec)
            model.docvecs.init_sims()
            return model
        return None

    @doc2vec.setter
    def doc2vec(self, doc2vec:Doc2Vec):
        doc2vec.save(self.__doc2vec)

    # UTILS
    def as_dict(self) -> dict:
        return dict(
            userId          = self.userId,
            corpus          = [doc.as_dict() for doc in self.corpus],
            graph           = self.graph,
            tsne            = self.tsne,
            umap            = self.umap)

    def clear_workspace(self):
        files = [
            self.__index,
            self.__graph,
            self.__tsne,
            self.__umap,
            self.__word2vec,
            self.__doc2vec]
        
        for f_path in files:
            if os.path.isfile(f_path):
                os.remove(f_path)


class Document:
    def __init__(self, userId:str, id:str):
        self.__userId = userId
        self.id = id

        self.__path = f"./users/{self.__userId}/corpus/{self.id}.json"

        if not os.path.isfile(self.__path):
            return None
        
        with open(self.__path, "r") as jsonFile:
            doc = json.load(jsonFile, encoding="utf-8")
            self._file_name      = doc["file_name"]
            self._content        = doc["content"]
            self._processed      = doc["content"]
            self._term_frequency = doc["term_frequency"]
            self._embedding      = doc["embedding"] if "embedding" in doc else None
            self._uploaded_on    = doc["uploaded_on"]

    # FILE NAME
    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name:str):
        self._file_name = file_name
        doc = self.as_dict()
        doc["file_name"] = file_name
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # CONTENT
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content:str):
        self._content = content
        doc = self.as_dict()
        doc["content"] = content
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # PROCESSED
    @property
    def processed(self):
        return self._processed

    @processed.setter
    def processed(self, processed:str):
        self._processed = processed
        doc = self.as_dict()
        doc["processed"] = processed
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # TERM FREQUENCY
    @property
    def term_frequency(self):
        return self._term_frequency

    @term_frequency.setter
    def term_frequency(self, term_frequency:dict):
        self._term_frequency = term_frequency
        doc = self.as_dict()
        doc["term_frequency"] = term_frequency
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # EMBEDDING
    @property
    def embedding(self):
        return self._embedding

    @embedding.setter
    def embedding(self, embedding:list):
        self._embedding = embedding
        doc = self.as_dict()
        doc["embedding"] = embedding
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # UTILS
    def as_dict(self) -> dict:
        return dict(
            id              = self.id,
            file_name       = self._file_name,
            content         = self._content,
            processed       = self._processed,
            term_frequency  = self._term_frequency,
            embedding       = self._embedding,
            uploaded_on     = self._uploaded_on)
    
class Session:
    def __init__(self, userId:str, id:str):
        self.__userId = userId
        
        self.id = id
        self.__path = f"./users/{self.__userId}/sessions/{self.id}.json"

        if os.path.isfile(self.__path):
            with open(self.__path, "r") as jsonFile:
                self.name           = jsonFile["name"]
                self.notes          = jsonFile["notes"]
                self.graph          = jsonFile["graph"]
                self.force          = jsonFile["force"]
                self.controls       = jsonFile["controls"]
                self.date           = jsonFile["date"]
            return self
        return None

    
    def as_dict(self) -> dict:
        return dict(
            id          = self.id,
            name        = self.name,
            notes       = self.notes,
            graph       = self.graph,
            force       = self.force,
            controls    = self.controls,
            date        = self.date)
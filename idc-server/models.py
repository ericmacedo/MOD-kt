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
        self.__user         = f"./users/{self.userId}"
        self.__corpus       = f"{self.__user}/corpus"
        self.__sessions     = f"{self.__user}/sessions"
        self.__graph        = f"{self.__user}/graph.json"
        self.__index        = f"{self.__user}/corpus.index"
        self.__tsne         = f"{self.__user}/tsne.npy"
        self.__word2vec     = f"{self.__user}/Word2Vec.bin"
        self.__doc2vec      = f"{self.__user}/Doc2Vec.bin"
        self.__settings     = f"{self.__user}/settings.json"
        self.__clusterer    = f"{self.__user}/doc_clusterer.bin"

        if not os.path.isdir(self.__user):
            return None

    @property
    def doc_model(self):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            if "doc_model" in settings:
                return settings["doc_model"]
        return None
    
    @doc_model.setter
    def doc_model(self, model:str):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            settings["doc_mode"] = model
        else:
            settings = dict(doc_model=model)
        
        with open(self.__settings, "w", encoding="utf-8") as f_settings:
            json.dump(settings, f_settings)

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
                        svg:str,
                        embedding:list=None) -> dict:

        uuid = str(uuid4())
        file_path = f"{self.__corpus}/{uuid}.json"

        document = {
            "id": uuid,
            "file_name": file_name,
            "content": content,
            "processed": processed,
            "term_frequency": term_frequency,
            "svg": svg,
            "uploaded_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC")}
        if embedding:
            document["embedding"] = embedding

        with open(file_path, "w", encoding="utf-8") as out_file:
            json.dump(document, out_file)
        
        with open(self.__index, "a") as index_file:
            index_file.write(f"{uuid}\n")
        
        return document

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
    
    def append_session(self,
                        name:str,
                        notes:str,
                        index:list,
                        graph:dict,
                        tsne:list,
                        controls:dict) -> dict:

        sessionId = str(uuid4())
        session_path = f"{self.__sessions}/{sessionId}.json"
        
        session = dict(
            id          = sessionId,
            name        = name,
            notes       = notes,
            index       = index,
            graph       = graph,
            tsne        = tsne,
            controls    = controls,
            date        = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC"))

        with open(session_path, "w", encoding="utf-8") as s_file:
            json.dump(session, s_file)

        return session
    
    def delete_sessions(self, ids:list):
        for f_path in os.listdir(self.__sessions):
            id, ext = os.path.splitext(f_path)
            if ext == ".json" and id in ids:
                os.remove(f"{self.__sessions}/{f_path}")

    def session_list(self):
        return [{
            "id":       session.id,
            "name":     session.name,
            "date":     session.date,
            "notes":    session.notes
        } for session in self.sessions]

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
            tsne            = self.tsne)

    def clear_workspace(self):
        files = [
            self.__index,
            self.__graph,
            self.__tsne,
            self.__word2vec,
            self.__doc2vec,
            self.__settings,
            self.__clusterer]
        
        for f_path in files:
            if os.path.isfile(f_path):
                os.remove(f_path)
    
        for f_path in os.listdir(self.__corpus):
            id, ext = os.path.splitext(f_path)
            if ext == ".json":
                os.remove(f"{self.__corpus}/{f_path}")
    
    def userData(self) -> dict:
        return {
            "userId":   self.userId,
            "corpus":   [doc.as_dict() for doc in self.corpus if doc],
            "sessions": self.session_list()}

    def sessionData(self, sessionId:str=None) -> dict:
        if sessionId:
            session = Session(
                userId=self.userId,
                sessionId=sessionId
            ).as_dict()
            session["sessions"] = self.session_list()
        else:
            session = {
                "userId":   self.userId,
                "name":     "Default",
                "notes":    "",
                "index":    self.index,
                "graph":    self.graph,
                "tsne":     self.tsne,
                "controls": {
                    "projection": "t-SNE",
		            "tsne": {"perplexity": 30},
                    "distance": 0.1,
                    "n_neighbors": 0,
                    "linkDistance": 20,
                    "charge": -30},
                "date": None}
        return session


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
            self._processed      = doc["processed"]
            self._term_frequency = doc["term_frequency"]
            self._embedding      = doc["embedding"] if "embedding" in doc else None
            self._uploaded_on    = doc["uploaded_on"]
            self.__svg           = doc["svg"]

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

    # SVG
    @property
    def svg(self):
        return self._svg
    
    @svg.setter
    def svg(self, svg:str):
        self._svg = svg
        doc = self.as_dict()
        doc["svg"] = svg
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
            svg             = self.__svg,
            uploaded_on     = self._uploaded_on)

    
class Session:
    def __init__(self, userId:str, id:str):
        self.__userId = userId
        
        self.id = id
        self.__path = f"./users/{self.__userId}/sessions/{self.id}.json"

        if not os.path.isfile(self.__path):
            return None
        with open(self.__path, "r") as jsonFile:
            session = json.load(jsonFile)
            self.name           = session["name"]
            self.notes          = session["notes"]
            self.index          = session["index"]
            self.graph          = session["graph"]
            self.tsne           = session["tsne"]
            self.controls       = session["controls"]
            self.date           = session["date"]

    def as_dict(self) -> dict:
        return dict(
            id          = self.id,
            name        = self.name,
            notes       = self.notes,
            index       = self.index,
            graph       = self.graph,
            tsne        = self.tsne,
            controls    = self.controls,
            date        = self.date)
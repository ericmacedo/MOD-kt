import os
import json
import threading
import numpy as np
from uuid import uuid4
from datetime import datetime
from importlib.util import (
    spec_from_file_location,
    module_from_spec)
import pathlib
from models import ModelType
from models.document import Document
from models.session import Session


class User:
    def __init__(self, userId: str):
        self.userId = userId

        # PATHS
        self.__user = os.path.abspath(f"./users/{self.userId}")
        self.__corpus = f"{self.__user}/corpus"
        self.__sessions = f"{self.__user}/sessions"
        self.__graph = f"{self.__user}/graph.json"
        self.__index = f"{self.__user}/corpus.index"
        self.__tsne = f"{self.__user}/tsne.npy"
        self.__settings = f"{self.__user}/settings.json"
        self.__clusterer = f"{self.__user}/doc_clusterer.bin"

        if not os.path.isdir(self.__user):
            return None
        else:
            pathlib.Path(self.__sessions).mkdir(parents=True, exist_ok=True)
            pathlib.Path(self.__corpus).mkdir(parents=True, exist_ok=True)

    @property
    def doc_model(self):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            if "doc_model" in settings:
                return settings["doc_model"]
        return None

    @doc_model.setter
    def doc_model(self, model: str):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            settings["doc_model"] = model
        else:
            settings = dict(doc_model=model)

        with open(self.__settings, "w", encoding="utf-8") as f_settings:
            json.dump(settings, f_settings)

    @property
    def word_model(self):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            if "word_model" in settings:
                return settings["word_model"]
        return None

    @word_model.setter
    def word_model(self, model: str):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            settings["word_model"] = model
        else:
            settings = dict(word_model=model)

        with open(self.__settings, "w", encoding="utf-8") as f_settings:
            json.dump(settings, f_settings)

    @property
    def isProcessed(self):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            if "isProcessed" in settings:
                return settings["isProcessed"]
        return False

    @isProcessed.setter
    def isProcessed(self, isProcessed: bool):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            settings["isProcessed"] = isProcessed
        else:
            settings = dict(isProcessed=isProcessed)

        with open(self.__settings, "w", encoding="utf-8") as f_settings:
            json.dump(settings, f_settings)

    @property
    def stop_words(self):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            if "stop_words" in settings:
                return settings["stop_words"]
        return []

    @stop_words.setter
    def stop_words(self, stop_words: list):
        if os.path.isfile(self.__settings):
            with open(self.__settings, "r", encoding="utf-8") as f_settings:
                settings = json.load(f_settings)
            settings["stop_words"] = stop_words
        else:
            settings = dict(stop_words=stop_words)

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

    @index.setter
    def index(self, index: list):
        np.savetxt(self.__index,
                   index,
                   encoding="utf-8",
                   fmt="%s",
                   newline="\n")

    def generate_index(self) -> list:
        ids = []
        for file in os.listdir(self.__corpus):
            id, ext = os.path.splitext(file)
            if ext == ".json":
                ids.append(id)
        ids.sort()

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
                        file_name: str,
                        content: str,
                        term_frequency: dict = None,
                        processed: str = None,
                        embedding: list = None) -> dict:

        uuid = str(uuid4())
        file_path = f"{self.__corpus}/{uuid}.json"
        
        document = {
            "id": uuid,
            "file_name": file_name,
            "content": content,
            "uploaded_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC")}
        if embedding:
            document["embedding"] = embedding
        if term_frequency:
            document["term_frequency"] = term_frequency
        if processed:
            document["processed"] = processed

        with open(file_path, "w", encoding="utf-8") as out_file:
            json.dump(document, out_file)

        with open(self.__index, "a") as index_file:
            index_file.write(f"{uuid}\n")

        return document

    def delete_documents(self, ids: list):
        for f_path in os.listdir(self.__corpus):
            id, ext = os.path.splitext(f_path)
            if ext == ".json" and id in ids:
                os.remove(f"{self.__corpus}/{f_path}")

        index = self.index

        idx_to_remove = [i for i, id in enumerate(index) if id in ids]

        # INDEX UPDATE
        self.index = [
            item for idx, item in enumerate(index)
            if not idx in idx_to_remove]
        del index

        # TSNE UPDATE
        tsne = self.tsne
        self.tsne = [
            item for idx, item in enumerate(tsne)
            if not idx in idx_to_remove]
        del tsne

        # GRAPH UPDATE
        graph = self.graph
        graph["nodes"] = [
            node for node in graph["nodes"]
            if not node["id"] in ids]
        graph["distance"] = [
            link for link in graph["distance"]
            if not (link["source"] in ids or link["target"] in ids)]
        graph["neighborhood"] = [
            link for link in graph["neighborhood"]
            if not (link["source"] in ids or link["target"] in ids)]
        self.graph = graph

    # SESSIONS
    @property
    def sessions(self):
        sessions = []

        for file in os.listdir(self.__sessions):
            id, ext = os.path.splitext(file)
            if ext == ".json":
                sessions.append(id)

        sessions.sort(key=lambda date: datetime.strptime(
            date,
            "{0}_%Y-%m-%d_%H:%M:%S".format(self.userId)))
        return [
            Session(userId=self.userId, id=id)
            for id in sessions]

    def append_session(self,
                       name: str,
                       notes: str,
                       index: list,
                       graph: dict,
                       clusters: dict,
                       tsne: list,
                       controls: dict,
                       selected: list,
                       focused: str,
                       highlight: str,
                       word_similarity: dict) -> dict:

        id = datetime.utcnow().strftime(
            "{0}_%Y-%m-%d_%H:%M:%S".format(self.userId))
        session_path = f"{self.__sessions}/{id}.json"

        session = dict(
            id=id,
            name=name,
            notes=notes,
            index=index,
            graph=graph,
            clusters=clusters,
            tsne=tsne,
            controls=controls,
            selected=selected,
            focused=focused,
            highlight=highlight,
            word_similarity=word_similarity,
            date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC"))

        # ASYNC
        t = threading.Thread(target=User.async_write,
                             args=(session_path, session))
        t.start()

        return session

    def delete_sessions(self, ids: list):
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
    def graph(self, graph: dict):
        # ASYNC
        t = threading.Thread(target=User.async_write,
                             args=(self.__graph, graph))
        t.start()

    # TSNE
    @property
    def tsne(self) -> list:
        if os.path.isfile(self.__tsne):
            return np.load(self.__tsne).tolist()
        return None

    @tsne.setter
    def tsne(self, tsne):
        np.save(self.__tsne, np.array(tsne, dtype=np.float64))

    @property
    def word_vectors(self):
        return self.__model(
            model_type=ModelType.WORD,
            name=self.word_model)

    @property
    def doc_vectors(self):
        return self.__model(
            model_type=ModelType.DOCUMENT,
            name=self.doc_model)

    # UTILS
    def __model(self, model_type: ModelType, name: str):
        spec = spec_from_file_location(
            name,
            f"./models/{model_type.value}/{name}.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def train(self) -> list:
        for vector in [self.word_vectors, self.doc_vectors]:
            vector.train_model(
                userId=self.userId,
                corpus=[doc.processed
                        for doc in self.corpus])

        return self.doc_vectors.get_vectors(
            userId=self.userId,
            data=[doc.processed for doc in self.corpus])

    @classmethod
    def async_write(cls, path, data):
        # ASYNC FILE WRITTING
        # As files tends to getter bigger and bigger
        # It writes the file in background
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file)

    def as_dict(self) -> dict:
        return dict(
            userId=self.userId,
            corpus=[doc.as_dict() for doc in self.corpus],
            graph=self.graph,
            tsne=self.tsne)

    def clear_workspace(self):
        files = [
            self.__index,
            self.__graph,
            self.__tsne,
            self.__settings,
            self.__clusterer]

        for f_path in files:
            if os.path.isfile(f_path):
                os.remove(f_path)

        for f_path in os.listdir(self.__corpus):
            id, ext = os.path.splitext(f_path)
            if ext == ".json":
                os.remove(f"{self.__corpus}/{f_path}")

        for f_path in os.listdir(self.__sessions):
            id, ext = os.path.splitext(f_path)
            if ext == ".json":
                os.remove(f"{self.__sessions}/{f_path}")

    def userData(self) -> dict:
        return {
            "userId":       self.userId,
            "corpus":       [doc.as_dict() for doc in self.corpus if doc],
            "sessions":     self.session_list(),
            "isProcessed":  self.isProcessed,
            "stop_words":    self.stop_words}

    def sessionData(self, id: str = None) -> dict:
        if id:
            session = Session(
                userId=self.userId,
                id=id
            ).as_dict()
            session["sessions"] = self.session_list()
        else:
            session = {
                "id":       None,
                "userId":   self.userId,
                "name":     "Default",
                "notes":    "",
                "index":    self.index,
                "graph":    self.graph,
                "clusters": {
                    "cluster_names": [],
                    "colors": [],
                    "cluster_words": [],
                    "cluster_docs": [],
                    "cluster_k": None
                },
                "tsne":     self.tsne,
                "controls": {
                    "projection": "t-SNE",
                    "tsne": {"perplexity": 30},
                    "link_selector": "Distance fn",
                    "distance": 0.1,
                    "n_neighbors": 0,
                    "linkDistance": 20,
                    "charge": -30},
                "date": None,
                "selected": [self.index[0]],
                "focused": self.index[0],
                "highlight": "",
                "word_similarity": {
                    "query": [],
                    "most_similar": []
                }}
        return session

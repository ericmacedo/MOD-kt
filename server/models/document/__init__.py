import os
import json


class Document:
    def __init__(self, userId: str, id: str):
        self.__userId = userId
        self.id = id

        self.__path = f"./users/{self.__userId}/corpus/{self.id}.json"

        if not os.path.isfile(self.__path):
            return None

        with open(self.__path, "r") as jsonFile:
            doc = json.load(jsonFile, encoding="utf-8")
            self._file_name = doc["file_name"]
            self._content = doc["content"]
            self._processed = doc["processed"] if "processed" in doc else None
            self._term_frequency = doc["term_frequency"] if "term_frequency" in doc else None
            self._embedding = doc["embedding"] if "embedding" in doc else None
            self._uploaded_on = doc["uploaded_on"]

    # FILE NAME
    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name: str):
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
    def content(self, content: str):
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
    def processed(self, processed: str):
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
    def term_frequency(self, term_frequency: dict):
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
    def embedding(self, embedding: list):
        self._embedding = embedding
        doc = self.as_dict()
        doc["embedding"] = embedding
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # UTILS
    def as_dict(self) -> dict:
        return dict(
            id=self.id,
            file_name=self._file_name,
            content=self._content,
            processed=self._processed,
            term_frequency=self._term_frequency,
            embedding=self._embedding,
            uploaded_on=self._uploaded_on)

def infer_doc2vec(data: str, **kwargs) -> list:
    model = kwargs.get("model", None)
    return model.infer_vector(
        data.split(" "), steps=35
    ) if model else None
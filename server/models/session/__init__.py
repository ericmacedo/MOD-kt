import os
import json


class Session:
    def __init__(self, userId: str, id: str):
        self.__userId = userId

        self.id = id
        self.__path = f"./users/{self.__userId}/sessions/{self.id}.json"

        if not os.path.isfile(self.__path):
            return None
        with open(self.__path, "r") as jsonFile:
            session = json.load(jsonFile)
            self.id = session["id"]
            self.name = session["name"]
            self.notes = session["notes"]
            self.index = session["index"]
            self.graph = session["graph"]
            self.clusters = session["clusters"]
            self.tsne = session["tsne"]
            self.controls = session["controls"]
            self.selected = session["selected"]
            self.focused = session["focused"]
            self.highlight = session["highlight"]
            self.word_similarity = session["word_similarity"]
            self.date = session["date"]

    def as_dict(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            notes=self.notes,
            index=self.index,
            graph=self.graph,
            clusters=self.clusters,
            tsne=self.tsne,
            controls=self.controls,
            selected=self.selected,
            focused=self.focused,
            highlight=self.highlight,
            word_similarity=self.word_similarity,
            date=self.date)

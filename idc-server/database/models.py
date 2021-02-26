from .db import db
from datetime import datetime
from uuid import uuid4

from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    DictField,
    ListField,
    FloatField,
    BinaryField,
    EmbeddedDocumentField)


class EmbDocument(EmbeddedDocument):
    id              = StringField(required=True, primary_key=True)
    file_name       = StringField(required=True, unique=False)
    content         = StringField(required=True, unique=False)
    processed       = StringField(required=True, unique=False)
    term_frequency  = DictField(required=True, unique=False)
    embedding       = ListField(FloatField(), required=False, unique=False)
    uploaded_on     = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC")

    def as_dict(self) -> dict:
        return dict(
            id              = self.id,
            file_name       = self.file_name,
            content         = self.content,
            processed       = self.processed,
            term_frequency  = self.term_frequency,
            embedding       = self.embedding,
            uploaded_on     = self.uploaded_on)
    


class User(Document):
    userId      = StringField(required=True, primary_key=True)
    corpus      = ListField(EmbeddedDocumentField(EmbDocument),
                            required=False, unique=False)
    graph       = DictField(required=False, unique=False)
    tsne        = ListField(FloatField(), required=False, unique=False)
    umap        = ListField(FloatField(), required=False, unique=False)
    word2vec    = BinaryField(required=False, unique=False)

    def as_dict(self) -> dict:
        return dict(
            userId          = self.userId,
            graph           = self.graph,
            tsne            = self.tsne,
            umap            = self.umap,
            word2vec        = self.word2vec)

    def corpus_tolist(self) -> list:
        return [doc.as_dict() for doc in self.corpus]

    def delete_documents(self, ids:list):
        self.update(corpus=[
            doc for doc in self.corpus if not doc.id in ids])

    def clear_workspace(self):
        self.graph      = None
        self.tsne       = None
        self.umap       = None
        self.word2vec   = None
        self.corpus     = []
        self.save()

def create_user(userId:str) -> User:
    from mongoengine import connect

    db = connect('idc', host='localhost', port=27017)

    user = User(userId=userId)
    user.save()

    db.close()
    return user
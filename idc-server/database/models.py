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
    
# class Session(EmbeddedDocument):
#     id              = StringField(required=True, primary_key=True)
#     name            = StringField(required=True, unique=False)
#     notes           = StringField(required=False, unique=False)
#     force           = DictField(required=False, unique=False)
#     controls        = DictField(required=False, unique=False)

#     def as_dict(self) -> dict:
#         return dict(
#             id          = self.id,
#             name        = self.name,
#             notes       = self.notes,
#             graph       = self.graph,
#             force       = self.force,
#             controls    = self.controls)

class User(Document):
    userId      = StringField(required=True, primary_key=True)
    corpus      = ListField(EmbeddedDocumentField(EmbDocument),
                            required=False, unique=False)
    ## TODO implement session management
    # sessions    = ListField(EmbeddedDocumentField(EmbDocument),
    #                         required=False, unique=False)
    graph       = DictField(required=False, unique=False)
    tsne        = ListField(FloatField(), required=False, unique=False)
    umap        = ListField(FloatField(), required=False, unique=False)
    word2vec    = BinaryField(required=False, unique=False)
    doc2vec     = BinaryField(required=False, unique=False)

    def as_dict(self) -> dict:
        return dict(
            userId          = self.userId,
            corpus          = self.corpus_tolist(),
            graph           = self.graph,
            tsne            = self.tsne,
            umap            = self.umap)

    def corpus_tolist(self) -> list:
        return [doc.as_dict() for doc in self.corpus]

    def delete_documents(self, ids:list):
        self.update(corpus=[
            doc for doc in self.corpus if not doc.id in ids])

    def clear_workspace(self):
        self.update(
            graph      = {},
            tsne       = [],
            umap       = [],
            word2vec   = None,
            corpus     = [])

def create_user(userId:str) -> User:
    from mongoengine import connect

    db = connect('idc', host='localhost', port=27017)

    user = User(userId=userId)
    user.save()

    db.close()
    return user
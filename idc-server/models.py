import json

class Corpus:
    @classmethod
    def add(cls, userId:str, file_name:str, content:str, processed:str):
        from datetime import datetime
        from uuid import uuid4

        uuid = str(uuid4())
        file_path = f"./users/{userId}/corpus/{uuid}.json"

        with open(file_path, "w", encoding="utf-8") as out_file:
            json.dump({
                "id": uuid,
                "file_name": file_name,
                "content": content,
                "processed": processed,
                "uploaded_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S-UTC")},
                out_file)

    @classmethod
    def delete(cls, userId:str, ids:list):
        import os

        corpus_path = f"./users/{userId}/corpus"

        if ids:
            for id in ids:
                os.remove(f"{corpus_path}/{id}.json")
        else:
            for filename in os.listdir(corpus_path):
                file_path = os.path.join(corpus_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)

    @classmethod
    def get_items(cls, userId:str, ids:list=[]) -> list:
        import os

        corpus_path = f"./users/{userId}/corpus"
    
        if not ids:
            ids = [
                file.split(".")[0] 
                for file in os.listdir(corpus_path)
                if file.endswith(".json")]

        documents = []
        for id in ids:
            file_path = f"{corpus_path}/{id}.json"
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as jsonFile:
                    documents.append(json.load(jsonFile))

        return documents
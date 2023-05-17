import os
import sys
import logging
import faulthandler
from dotenv import load_dotenv
from nltk import download as NLTK_Downloader

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

logging.basicConfig(filename=os.path.abspath("./log/server.log"),
                    level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

faulthandler.enable()

load_dotenv('.env')

# Data folders
os.environ["TOKENIZERS_PARALLELISM"] = "false"

NLTK_Downloader([
    "stopwords", "wordnet", "punkt",
    "averaged_perceptron_tagger"
], quiet=True)

from app import app  # noqa

def sanity_check() -> bool:
    from importlib.util import (
        spec_from_file_location,
        module_from_spec)

    base_attr = ["name", "model_path", "load_model",
                 "save_model", "train_model",
                 "get_vectors", "cluster"]
    m_type = {
        "word": base_attr + ["seed_paragraph", "most_similar"],
        "document": base_attr + []}
    try:
        for model in m_type.keys():
            m_type_dir = os.path.abspath(f"./models/{model}")

            models = [
                m_file for m_file in os.listdir(m_type_dir)
                if os.path.isfile(f"{m_type_dir}/{m_file}")
                and not m_file.startswith("_")
                and m_file.endswith(".py")]

            for m_file in models:
                spec = spec_from_file_location(
                    os.path.splitext(m_file)[0],
                    f"{m_type_dir}/{m_file}")
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                for attr in m_type[model]:
                    if not hasattr(module, attr):
                        msg = f"Attribute '{attr}' not implemented in file {os.path.abspath(m_file)}"
                        raise AttributeError(msg)
        sys.stdout.write("Configuration passed through sanity check\n")
    except AttributeError as e:
        sys.stdout.write(e)
        sys.stdout.write("System is exiting due misconfiguration\n")
        return False

    return True


if __name__ == "__main__":
    if sanity_check():
        import uvicorn

        uvicorn.run(app,
            host=os.environ.get("SERVER_HOST"),
            port=int(os.environ.get("SERVER_PORT")))
    else:
        sys.exit(0)

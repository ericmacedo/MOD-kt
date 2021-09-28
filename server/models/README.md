# Each model file **must** respect the following signature:

* `name:str`
  * Generally is the file's name
* `model_path(userId: str) -> str`
* `load_model(userId: str) -> MODEL_PKG`
  * Where `MODEL_PKG` is the `type` for the models
* `save_model(model: MODEL_PKG, userId: str)`
  * Where `MODEL_PKG` is the `type` for the models
* `train_model(userId: str, corpus: List[str]) -> MODEL_PKG`
  * Where `MODEL_PKG` is the `type` for the models;
  * And `corpus` is the corpus to be trained on
* `get_vectors(userId: str, corpus: List[str]) -> List`
  * And `corpus` is the corpus to be trained on
* `cluster(userId)`
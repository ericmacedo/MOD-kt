# i2DC - Interactive and Incremental Document Clustering

[![Ubuntu](https://img.shields.io/static/v1?label=Ubuntu&message=18.04&color=orange)]("https://releases.ubuntu.com/18.04/)
[![Docker](https://img.shields.io/static/v1?label=Docker&message=20.10.7&color=steelblue)](https://docs.docker.com/engine/release-notes/#20107)
[![Python](https://img.shields.io/static/v1?label=Python&message=3.6.9&color=yellow)](https://www.python.org/downloads/release/python-369/)
[![PyPi](https://img.shields.io/static/v1?label=PyPi&message=21.2.4&color=blue)](https://pypi.org/project/pip/21.2.4/)
[![NPM](https://img.shields.io/static/v1?label=npm&message=6.14.13&color=red)](https://www.npmjs.com/package/npm/v/6.14.13)
[![Node](https://img.shields.io/static/v1?label=Node.js&message=14.17.0&color=green)](https://nodejs.org/ca/blog/release/v14.17.0/)

There are two ways of running this system:

* **Standalone**: Runs directly in the host's system. Then, you must have install the dependencies:
    ```shell
    sudo apt-get -y update && \
    sudo apt-get -y install python3.6 python3-pip && \
    sudo apt-get -y install unzip wget curl virtualenv git \
    --no-install-recommends \
    --no-install-suggests
    ```
* **Container**: Runs the system in a Docker Container.
  * Follow [this link](https://docs.docker.com/get-docker/) for instructions on how to install Docker

# Instructions

## Standalone version

1. Create a `.env` in the folder of the project with the following variables:
    - `SYSTEM_PREFIX=/` (`/` is the default value)
    - `SERVER_DEBUG=`**`False`** if production, **`True`** if development
    - `SERVER_ENV=`**`development`**   or **`production`**
    - `SERVER_HOST=`**`localhost`** or **`0.0.0.0`** (`0.0.0.0` is the default value)
    - `SERVER_PORT=`**`12000`** (`12000` is the default value)
    - `SERVER_URL_PREFIX=${SYSTEM_PREFIX}` (must be exactly like the example)
    - `SERVER_SECRET_KEY=123456` (`123456` is the default value)
    - `VUE_APP_SERVER_PREFIX=${SYSTEM_PREFIX}` (must be exactly like the example)
    - `VUE_APP_SERVER_HOST=localhost` (`123456` is the default value)
2. Create virtual environment in `./venv/`:
    ```shell
    virtualenv --python=python3.6 ./venv/ --prompt="(IDC [Python + Node.js])"
    ```
3. Activate environment: 
    ```shell
    source ./venv/bin/activate
    ```
4. Install Python dependencies with **Pip**:
    ```shell
    pip install -r python_requirements.txt
    ```
5. Refresh environment:
    ```shell
    deactivate; source ./venv/bin/activate
    ```
6. Install **NodeEnv** on the existing environment:
    ```shell
    nodeenv --config-file=node_env.cfg --python-virtualenv
    ```
7. Create data folders for **Scikit Learn**, **NLTK** and **Sentence Transformers**:
    ```shell
    mkdir -p ./venv/data/scikit_learn \
    ./venv/data/nltk \
    ./venv/data/transformers
    ```
8.  Setup logging
    ```shell
    mkdir ./server/log
    touch ./server/log/access.log \
    ./server/log/error.log \
    ./server/log/server.log
    ```
9. Install Node dependencies:
    ```shell
    cd ./web && npm ci
    ```
10. Build front for production:
    ```shell
    npm run build --mode=production
    ```

### Running the server

* Serve it with some Python WSGI HTTP Server for UNIX, such as `Gunicorn`
* You must run the `./server/wsgi.py` file

Here's a example using `Gunicorn[uvicorn]`:
```shell
gunicorn \
    --name i2dc \
    --workers 6 \
    --threads 4 \
    --timeout 3600 \
    --bind 0.0.0.0:8000 \
    --forwarded-allow-ips "*" \
    --worker-class uvicorn.workers.UvicornWorker \
    wsgi:app
```
* Make sure you actiavated the environment and that you're in the `./server/` folder.

### Using NVIDIA GPU processing

> The following instructions were tested on Ubuntu 18.04 (Bionic Beaver).

* Make sure you have Cuda drivers installed and configured
* If you're Cuda ready, the system will recognize it and will use GPU processing

## Docker Container version

1. Create a `.env` in the folder of the project with the following variables:
    - `SYSTEM_PREFIX=/` (`/` is the default value)
    - `SERVER_DEBUG=`**`False`** if production, **`True`** if development
    - `SERVER_ENV=`**`development`**   or **`production`**
    - `SERVER_HOST=`**`localhost`** or **`0.0.0.0`** (`0.0.0.0` is the default value)
    - `SERVER_PORT=`**`12000`** (`12000` is the default value)
    - `SERVER_URL_PREFIX=${SYSTEM_PREFIX}` (must be exactly like the example)
    - `SERVER_SECRET_KEY=123456` (`123456` is the default value)
    - `VUE_APP_SERVER_PREFIX=${SYSTEM_PREFIX}` (must be exactly like the example)
    - `VUE_APP_SERVER_HOST=localhost` (`123456` is the default value)
2. Create the log files:
    ```
    mkdir -p ./server/log && \
    touch ./server/log/access.log \
    ./server/log/server.log \
    ./server/log/error.log
    ```

> Make sure you have Docker and Docker Compose installed for the next instructions

1. Run the command in the project's root folder:
    ```shell
    docker compose up
    ```
2. Now you can access the system through `http://SERVER_HOST:SERVER_PORT`
    - Being `SERVER_HOST` and `SERVER_PORT` the variables you provided in the `.env` file


### Using NVIDIA GPU processing

> The following instructions were tested on Ubuntu 18.04 (Bionic Beaver).<br/>
  If you're running it in a OS other than Linux, you need to search how to expose Cuda cores (if it is possible) to the Docker container.

* Make sure you have Cuda drivers installed and configured on the host
* Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installation-guide).

## Creating new users

Just create a folder with the username as its name under `./server/users`.
For instance, to create a user named `default`:
  ```shell
  mkdir ./server/default
  ```

## To do

*   [ ] Index Tutorial page (Component Index.vue)
*   [ ] Lasso selection on graph view
*   [ ] Stopwords manager
*   [ ] Change upload pipeline

# Know bugs

* Recluster is not working
* Unecessary links showing up o cluster highlighting

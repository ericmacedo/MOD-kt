# i2DC - Interactive and Incremental Document Clustering

<center>
  <strong>Tested on Ubuntu 18.04 (Bionic Beaver)</strong>
  <br/>
</center>

There are two ways of running this system:

* **Standalone**: Runs directly in the host's system. Then, you must have install the dependencies:
    ```shell
    # apt -y update
    # apt -y install python3.6 python3-pip 
    # apt -y install unzip wget curl virtualenv git \
      --no-install-recommends \
      --no-install-suggests
    ```
* **Container**: Runs the system in a Docker Container.
  * Follow [this link](https://docs.docker.com/get-docker/) for instructions on how to install Docker

# Instructions

## Standalone version

1. Set flask configs on `'./server/.env'` file:
    * `FLASK_DEBUG=`**`False`** if production, **`True`** if development
    * `FLASK_ENV=`**`development`**   or **`production`**
    * `FLASK_RUN_HOST=`**`localhost`** or **`0.0.0.0`**
    * `FLASK_RUN_PORT=`**`5000`**
    * `FLASK_SECRET_KEY=`**`YOUR_SECRET_KEY`**
2. Create virtual environment in `./env/`:
    ```shell
    $ virtualenv --python=python3.6 ./env/ --prompt="(IDC [Python + Node.js])"
    ```
3. Activate environment: 
    ```shell
    $ source ./env/bin/activate
    ```
4. Install Python dependencies with **Pip**:
    ```shell
    $ pip install -r python_requirements.txt
    ```
5. Refresh environment:
    ```shell
    $ deactivate; source ./env/bin/activate
    ```
6. Install **NodeEnv** on the existing environment:
    ```shell
    $ nodeenv --config-file=nodeenvrc --python-virtualenv
    ```
7. Create data folders for **Scikit Learn**, **NLTK** and **Sentence Transformers**:
    ```shell
    $ mkdir -p  ./env/data/scikit_learn \
              ./env/data/nltk \
              ./env/data/transformers
    ```
8.  Setup logging
    ```shell
    $ mkdir ./server/log
    $ touch ./server/log/access.log \
          ./server/log/error.log \
          ./server/log/flask.log
    ```
9. Set **Vue** configs on `'./web/.env.production'` file:
    * `VUE_APP_SERVER_URL=YOUR_URL` (with protocol, `http` or `https`)
    * `VUE_APP_SERVER_PORT=YOUR_PORT`
10. Install Node dependencies:
    ```shell
    $ cd ./web && npm install
    ```
11. Build ir for production:
    ```shell
    $ npm run build --mode=production
    ```

### Running the server

* Serve it with some Python WSGI HTTP Server for UNIX, such as `Gunicorn[gevent]`
* You must run the `./server/wsgi.py` file

Here's a example using `Gunicorn[gevent]`:
```shell
$ gunicorn \
    --workers 6 \
    --threads 4 \
    --timeout 3600 \
    --bind 0.0.0.0:12115 \
    wsgi:app
```
* Make sure you actiavated the environment and that you're in the `./server/` folder.

### Using NVIDIA GPU processing

> The following instructions were tested on Ubuntu 18.04 (Bionic Beaver).

* Make sure you have Cuda drivers installed and configured
* If you're Cuda ready, the system will recognize it and will use GPU processing

## Docker Container version

1. Create data folder for `Scikit Learn`, `NLTK` and `Transformers`:
    ```shell
      $ mkdir -p ./env/data/
      $ mkdir ./env/data/scikit_learn \
              ./env/data/nltk \
              ./env/data/transformers
    ```
2. Create the log files:
    ```
    $ mkdir -p ./server/log
    $ touch ./server/log/access.log \
            ./server/log/flask.log \
            ./server/log/error.log
    ```
3. Create the `./server/.env` file:
    ```shell
    $ echo \
    "FLASK_DEBUG=False
    FLASK_ENV=production
    FLASK_RUN_HOST=0.0.0.0
    FLASK_RUN_PORT=5000
    FLASK_SECRET_KEY=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 13)
    " > ./server/.env
    ```
4. Create `Vue` environment file:
    ```shell
    $ echo \
    "VUE_APP_SERVER_URL=http://127.0.0.1
    VUE_APP_SERVER_PORT=5000
    " > ./web/.env.production
    ```
5. Install `NPM` dependencies and build for production:
    ```shell
    $ cd ./web && npm install
    $ npm run build --mode=production
    ```

> Make sure you have Docker installed for the next instructions

1. Fetch needed base Docker images:
    ```shell
    $ docker pull nvidia/cuda:11.2.0-base-ubuntu18.04
    $ docker pull busybox
    ```
2. Create a volume for data storage copy repository to it:
    ```shell
    $ docker volume create i2dc
    $ docker run -v i2dc:/app --name helper busybox true
    $ docker cp . helper:/app
    $ docker rm helper
    ```
3. Build Container snapshot and name it:
    ```shell
    $ docker build -t i2dc .
    ```
    * Make sure you're in the root of this repository, where the `Dockerfile` is located

### Running the server

```shell
# docker run -dit i2dc \
    --name i2DC \
    --port 12115:12115 \
    --volume i2dc:/app
```

### Using NVIDIA GPU processing

> The following instructions were tested on Ubuntu 18.04 (Bionic Beaver).<br/>
  If you're running it in a OS other than Linux, you need to search how to expose Cuda cores (if it is possible) to the Docker container.

* Make sure you have Cuda drivers installed and configured on the host
* Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installation-guide). Then run:
    ```shell
    # docker run -dit i2dc \
        --name i2DC \
        --port 12115:12115 \
        --volume i2dc:/app \
        --gpus all
    ```

## To do

*   [ ] Index Tutorial page (Component Index.vue)
*   [ ] Lasso selection on graph view
*   [ ] Stopwords manager
*   [ ] Change upload pipeline

# Know bugs

* Recluster is not working
* Unecessary links showing up o cluster highlighting
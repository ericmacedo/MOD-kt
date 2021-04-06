# i2DC

## OS dependencies:
* Python3.6

* python3-pip python-virtualenv npm unzip wget rsync

# Setup

## Server
* Set flask configs on './server/.env' file
  * `FLASK_DEBUG`: `False` if production, `True` if development
  * `FLASK_ENV`: `development` or `production`
  * `FLASK_RUN_HOST`: `localhost` or `0.0.0.0`
  * `FLASK_RUN_PORT`: `5000`
  * `FLASK_SECRET_KEY`: YOUR_SECRET_KEY

1. `cd ./server`
2. `virtualenv --python=python3.6 .`
3. `source ./bin/activate`
4. `pip install -r requirements.txt`
5. Download and setup `allenai-specter` model
  1. `mkdir ./server/pre-trained`
  2. `wget https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/allenai-specter.zip`
  3. `unzip ./server/allenai-specter -d ./server/pre-trained/allenai-specter; rm ./server/allenai-specter.zip`
6. Setup logging
   1. `mkdir ./server/log`
   2. `touch ./server/log/access.log ./server/log/error.log ./server/log/flask.log`
7. Serve it with some Python WSGI HTTP Server for UNIX, such as Gunicorn[gevent]

## Web
* Set Vue configs on './web/.env.production' file:
  * `VUE_APP_SERVER_URL`: YOUR_URL
  * `VUE_APP_SERVER_PORT`: YOUR_PORT

1. `cd ./web`
2. `npm install`
3. `npm run build --mode=production`

# To do
*   [ ] Index Tutorial page (Component Index.vue)
*   [ ] Lasso selection on graph view
*   [ ] Stopwords manager
*   [ ] Change upload pipeline

# Know bugs
* Recluster is not working
* Unecessary links showing up o cluster highlighting
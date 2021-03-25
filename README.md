# i2DC

## OS dependencies:
* Python3.6

* python3-pip python-virtualenv npm

# Setup

## Server
* Set flask configs on './server/.env' file
  * `FLASK_DEBUG`: `False` if production, `True` if development
  * `FLASK_ENV`: `development` or `production`
  * `FLASK_RUN_HOST`: `localhost` or `0.0.0.0`
  * `FLASK_RUN_PORT`: `5000`
  * `FLASK_SECRET_KEY`: YOUR_SECRET_KEY

## Web
* Set Vue configs on './web/.env.production' file:
  * `VUE_APP_SERVER_URL`: YOUR_URL
  * `VUE_APP_SERVER_PORT`: YOUR_PORT

# To do
*   [ ] Index Tutorial page (Component Index.vue)
*   [ ] Lasso selection on graph view
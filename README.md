
# Capital

* ```git clone https://github.com/artur0527rg/AdminLTE-Capital.git```

* ```cd AdminLTE-Capital```
* ```python -m venv .venv```
* ```. .venv/bin/activate```
* ```pip install -r requirements.txt```
* ```pip install "Your db client"```
* Create an .env file and set the following variables.
  * DEBUG
  * DB_ENGINE
  * DB_HOST
  * DB_NAME
  * DB_USERNAME
  * DB_PASS
  * DB_PORT
* ```gunicorn --config gunicorn-cfg.py core.wsgi```
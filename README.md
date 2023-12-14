
# Capital

* ```git clone https://github.com/artur0527rg/AdminLTE-Capital.git```

* ```cd AdminLTE-Capital```
* ```python -m venv .venv```
* ```. .venv/bin/activate```
* ```pip install -r requirements.txt```
* ```pip install "Your db client"```
* ```python manage.py migrate```
* ```python manage.py loaddata categoryofcompany```
* ```python manage.py collectstatic```
* Create an .env file and set the following variables.
  * DEBUG
  * DB_ENGINE
  * DB_HOST
  * DB_NAME
  * DB_USERNAME
  * DB_PASS
  * DB_PORT
* Configure nginx
* ```gunicorn --config gunicorn-cfg.py core.wsgi```
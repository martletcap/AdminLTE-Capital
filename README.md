
# Capital

* ```git clone https://github.com/artur0527rg/AdminLTE-Capital.git```

* ```cd AdminLTE-Capital```
* ```python3 -m venv .venv```
* ```. .venv/bin/activate```
* ```pip install -r requirements.txt```
* ```pip install "Your db client"```
* ```python manage.py migrate```
* ```python manage.py loaddata companystatus portfolio transactiontype location contacttype contact categoryofcompany```
* ```python manage.py collectstatic```
* Create an .env file and set the following variables.
  * DEBUG
  * DB_ENGINE
  * DB_HOST
  * DB_NAME
  * DB_USERNAME
  * DB_PASS
  * DB_PORT
  * COMPANY_HOUSE_KEY
  * CELERY_BROKER_URL
* Configure nginx
* ```gunicorn --config gunicorn-cfg.py core.wsgi```
* ```celery -A core worker -l INFO```
* ```celery -A core beat -l INFO```
# webtrader
Django webui application to explore data

## Prerequisits and setup
To create our environment we use pipenv.
Make sure you have python3 installed (last version sine python 2 is deprecated)
```bash
python --version
Python 3.7.3
```
Last command should returned something like Python 3.7.x.

After, install pip and pipenv :

```bash
python -m pip install pip
python -m pip install pipenv
```
Create your virtualenv for dashboard
```bash
cd webtrader/dashboard
pipenv shell
```
Now you're ok to start the project, we supposed you already have cloned this repo. Last to do before launch python projet is to pull all dependances :
```bash
pip install -r requirements.txt
```
Now try to launch after initiation
```bash
python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser
python manage.py runserver
```

## Django Dev

To revert project due to too many modifications that have corrupted the database and the code :
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -name "admin_sqlite.py" -delete && find . -path "*/migrations/*.pyc"  -delete && rm -f db.sqlite3
python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser
python manage.py runserver
```

## Django api project


## Django dashboard project


## Django admin project


> Written with [StackEdit](https://stackedit.io/).
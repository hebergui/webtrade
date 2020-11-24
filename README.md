# webtrader
Django webui application to explore financial data (mainly Stan Weinstein methods)

## Prerequisits and setup
We use [Virtualenv](http://pypi.org/project/virtualenv) because it's a great tool to create isolated Python environments : it creates a folder which contains all the necessary executables to use the packages that a Python project would need.

1. Make sure you have python3 installed (last version sine python 2 is deprecated)
```bash
python --version
Python 3.x.x
```
2. After, install pip and virtualenv :
```bash
python -m pip install pip
python -m pip install virtualenv
```
3. Create your virtualenv for dashboard in "venv" directory
```bash
cd webtrader
python -m virtualenv -p /usr/bin/python3 venv 
```
4. To begin using the virtual environment, it needs to be activated:
```bash
source venv/bin/activate
(deactivate : when you are done working in the virtual environment)
```
5. Now you're ok to start the project, we supposed you already have cloned this repo. Last thing to do before launching django app is to pull all dependancies :
```bash
python -m pip install -r requirements.txt
```
6. Running time
```bash
python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
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

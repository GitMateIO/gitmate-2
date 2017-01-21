GitMate 2
=========

The new version of GitMate - written in django!

What exactly is GitMate?
------------------------

GitMate is a software which listens for certain events in your git project
(e.g. push event) and runs a plugin (which you have configured) when that event
is detected.

So what can GitMate do?
--------------------

**Anything!** In gitmate different plugins perform different functions that you
can choose from. If you can't find a plugin you are looking for
you can make your own!

Running the Project
-------------------

Make sure bower as well as a virtual environment with pip is available:

```
virtualenv ~/.venvs/coon
. ~/.venvs/coon/bin/activate
npm install bower
```

Now install the project specific requirements and create your initial database:

```
pip install -r requirements.txt
bower install
python3 manage.py migrate
```

Followed by updating the database with all configured GitMate plugins:

```
python3 manage.py upmate
```

Now you can run the actual server:

```
python3 manage.py runserver
```

Testing
-------

Tests can be run with

```
python3 manage.py test
```

The code analysis can be run in the
[official coala container](http://docs.coala.io/en/latest/Users/Docker_Image.html)
or locally when installing the ``coala-bears`` pip package:

```
coala
```

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

Make sure virtual environment with pip is available:

```
virtualenv ~/.venvs/coon
. ~/.venvs/coon/bin/activate
```

Now install the project specific requirements and create your initial database:

```
pip install -r requirements.txt
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

Modifications to Models
-----------------------

After adding/removing models in apps, you would need to make migrations
for the database. You could make migrations with

```
python3 manage.py makemigrations
```

And then migrate the changes with
```
python3 manage.py migrate
```

Accessing Django shell
----------------------

To run a python interpreter with a complete django environment setup,
just run

```
python3 manage.py shell
```

Accessing Django's database(via an SQL shell)
---------------------------------------------
We could access the database through SQL commands via a shell, to
do so, just run

```
python3 manage.py dbshell
```

Collecting static assets into wsgi application(production stage)
----------------------------------------------------------------
We could collect all static files into a single location so they
could be served easily in production.

```
python3 manage.py collectstatic
```

Clear sessions
--------------
Ever got caught in an irksome situation, without a logout button?
You could end all your sessions with,

```
python manage.py clearsessions
```

Social Authentication
---------------------
**Providers Supported:**
    - GitLab (OAuth2)
    - GitHub (OAuth2)
    - Bitbucket (OAuth)

Please include your CLIENT ID and CLIENT SECRET keys in
`gitmate/settings.py`.

The login URL: `<domainname:port>/auth/login/<provider>`

This saves the required access tokens as provided by the providers
into the `User` model, which could later be used to send
authenticated requests to communicate with the providers.

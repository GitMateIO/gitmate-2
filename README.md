GitMate 2
=========

The new version of GitMate - written in django!

What exactly is GitMate?
------------------------

GitMate is a software which listens for certain events in your git project
(e.g. push event) and runs a plugin (which you have configured) when that event
is detected.

So what can GitMate do?
-----------------------

**Anything!** In gitmate different plugins perform different functions that you
can choose from. If you can't find a plugin you are looking for
you can make your own!

Requirements
============

Development requirements
------------------------

- python3 (v3.5 or later recommended)
- django (v1.9 or later)
- postgresql: database backend for gitmate
- celery: Asynchronous Task Processing queue for gitmate webhook responders


Production requirements
-----------------------

*All the development requirements plus the ones below.*

- rabbitmq: Message broker for celery


Requirements for unit-testing and linting
-----------------------------------------

- pytest (unit-testing)
- pytest-cov
- pytest-django
- docutils
- coala (linter)


Configuring Environment Variables
---------------------------------

- `DJANGO_DEBUG`: Run django in debug mode
    - default: `False`
- `DJANGO_SECRET_KEY`: Cryptographic signing for django
    - details: [Django documentation](
        https://docs.djangoproject.com/en/1.11/ref/settings/#secret-key)
- `DJANGO_ALLOWED_HOSTS`: Allowed hosts for django
- `DB_NAME`: Database name for postgresql
    - default: `postgres`
    - details: Auto-configured database name
- `DB_USER`: Database username for postgresql
    - default: `postgres`
    - details: Auto-configured username
- `DB_PASSWORD`: Database password for postgresql
    - default: ``
    - details: No password for fresh install
- `DB_ADDRESS`: Database host address for postgresql
    - default: ``
    - details: Auto-configured via socket on `/run/postgresql`
- `DB_PORT`: Database server port for postgresql
    - default: ``
    - details: Auto-configured for port `5432`
- `DJANGO_STATIC_ROOT`: Directory for storing django static files.
    - default: `/tmp/static`
- `CELERY_BROKER_URL`: URI for celery broker
    - default: `amqp://admin:password@rabbit/`
- `SOCIAL_AUTH_LOGIN_REDIRECT_URL`: URL to be redirected to, after
 authentication
- `SOCIAL_AUTH_GITHUB_KEY`: Client key for GitHub OAuth Application
- `SOCIAL_AUTH_GITHUB_SECRET`: Client secret for GitHub OAuth Application
- `GITHUB_WEBHOOK_SECRET`: A secret key to register GitHub
webhooks with, improves security.

> Note: Make sure all the services like rabbitmq, postgresql, etc. are running.
> before running the project. Refer their docs on how to set them up.

Running gitmate
---------------

Make sure virtual environment with pip is available:

```bash
virtualenv ~/.venvs/coon
. ~/.venvs/coon/bin/activate
```

To run GitMate you'll need a secret. Use any string you can come up with:

```bash
export GITHUB_WEBHOOK_SECRET=foobar
```

Now install the project specific requirements and create your initial database:

```bash
pip install -r requirements.txt
python3 manage.py migrate
```

Followed by updating the database with all configured GitMate plugins:

```bash
python3 manage.py upmate
```

Start the development server:

```bash
./start_debug_server
```

Setting up Celery with Rabbitmq
===============================
* `sudo rabbitmq-server start`: turns on the rabbitmq server.
* `python3 manage.py migrate`: run migrations, if any.
* `python3 manage.py celeryd --loglevel=info
    --logfile=/var/log/celery/gitmate.log
    --settings='gitmate.settings'`: starts celery service.
* Run django server.

> Any permission errors related to logfiles could be handled by executing
`sudo chown <username> --recursive /var/log/celery`. Also create the file,
`/var/log/celery/gitmate.log`.


Unit Testing
------------

Tests can be run with

```bash
py.test --cov --doctest-modules -vv
```

The code analysis can be run in the [official coala container](
http://docs.coala.io/en/latest/Users/Docker_Image.html) or locally when
installing the ``coala-bears`` pip package:

```bash
coala
```

Creating a new plugin
---------------------

Create a new plugin with the name `<name_of_plugin>`.

```bash
python3 manage.py startplugin <name_of_plugin>
```

Add the plugin to `GITMATE_PLUGINS` in `gitmate/settings.py`.

Modifications to Models
-----------------------

After adding/removing models in apps, you would need to make migrations
for the database. You could make migrations with

```bash
python3 manage.py makemigrations
```

And then migrate the changes with
```bash
python3 manage.py migrate
```

Accessing Django shell
----------------------

To run a python interpreter with a complete django environment setup,
just run

```bash
python3 manage.py shell
```

Accessing Django's database(via an SQL shell)
---------------------------------------------
We could access the database through SQL commands via a shell, to
do so, just run

```bash
python3 manage.py dbshell
```

Collecting static assets into wsgi application(production stage)
----------------------------------------------------------------
We could collect all static files into a single location so they
could be served easily in production.

```bash
python3 manage.py collectstatic
```

Clear sessions
--------------
Ever got caught in an irksome situation, without a logout button?
You could end all your sessions with,

```bash
python manage.py clearsessions
```

Social Authentication
---------------------
**Providers Supported:**
- GitLab (OAuth2)
- GitHub (OAuth2)
- Bitbucket (OAuth)

The login URL: `<domainname:port>/auth/login/<provider>`

This saves the required access tokens as provided by the providers
into the `User` model, which could later be used to send
authenticated requests to communicate with the providers.

Documentation to API Endpoints
------------------------------
The docs could be accessed via http://localhost:8000/docs once the server is
running.

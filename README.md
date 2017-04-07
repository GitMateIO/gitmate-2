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

To run GitMate you'll need a secret. Use any string you can come up with:

```
export GITHUB_WEBHOOK_SECRET=foobar
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

Now change to the "fronted" Directory and install the frontend dependencies:

```
cd frontend
npm install
./node_modules/typings/dist/bin.js install dt~hammerjs --global
```

Compile the app once, or continuously on filechange:

```
npm run tsc   # one-shot compilation
npm run tsc:w # continuous compilation
```

Now you can go back to the "gitmate-2" dir and run the server:

```
cd ..
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


Frontend Unit Tests
-------------------
TypeScript unit-tests are usually in the `app` folder. Their filenames must end in `.spec`.

Look for the example `app/app.component.spec.ts`.
Add more `.spec.ts` files as you wish; we configured karma to find them.

Run it with `npm test`

That command first compiles the application, then simultaneously re-compiles and runs the karma test-runner.
Both the compiler and the karma watch for (different) file changes.

Shut it down manually with `Ctrl-C`.

Test-runner output appears in the terminal window.
We can update our app and our tests in real-time, keeping a weather eye on the console for broken tests.
Karma is occasionally confused and it is often necessary to shut down its browser or even shut the command down (`Ctrl-C`) and
restart it. No worries; it's pretty quick.


Testing (development)
=====================
*both frontend and backend combined*

You could test the full app, by following these steps.

* `cd frontend` : change directory into frontend
* `npm run tsc` : compile the app once (`npm run tsc:w` for coninuous compilation)
* `cd ..` : change directory back into the root
* `python3 manage.py runserver` : runs the server for testing

Navigate to `http://localhost:8000/` to see the application running.

> Note that the link `/static/` specified as STATIC_URL in `gitmate/settings.py` links the static serve of files, so all static links
> in `frontend/index.html` should prefix the same, and the `baseURL` settings
> of `frontend/system.config.js` should reflect the same, for proper functioning of the application.

Documentation to API Endpoints
------------------------------
The docs could be accessed via http://localhost:8000/docs once the server is running.

Setting up Celery with Rabbitmq
===============================

Requirements
------------
- celery: Asynchronous Task Processing queue based on distributed message processing
- rabbitmq: Message broker for celery

Configuration
-------------
* Add `BROKER_URL` in `gitmate/settings.py`.
* `sudo rabbitmq-server start`: turns on the rabbitmq server.
* `python3 manage.py migrate`: run migrations, if any.
* `python3 manage.py celeryd --loglevel=info --logfile=/var/log/celery/gitmate.log`: starts celery service.
* Run django server.

> Any permission errors related to logfiles could be handled by executing
`sudo chown <username> --recursive /var/log/celery`. Also create the file,
`/var/log/celery/gitmate.log`.


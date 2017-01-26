Backend
=======

GitMate 2 Backend
=================

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


Frontend
========

GitMate 2 Frontend
==================

Frontend for the new version of GitMate

> `cd frontend` - change into frontend directory to work with the frontend

Trying it out:
--------------

* `npm install` - installs the prerequisited from the `package.json` file
* `npm start` - runs the compiler and a server at the same time, both in "watch mode".
* `npm run tsc` - runs the TypeScript compiler once.
* `npm run tsc:w` - runs the TypeScript compiler in watch mode; the process keeps running, awaiting changes to TypeScript files and re-compiling when it sees them.
* `npm run lite` - runs the [lite-server](https://www.npmjs.com/package/lite-server), a light-weight, static file server, written and maintained by
[John Papa](https://github.com/johnpapa) and
[Christopher Martin](https://github.com/cgmartin)
with excellent support for Angular apps that use routing.
* `npm test` - compiles, runs and watches the karma unit tests

Unit Tests
----------
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
* `npm run tsc` : compile the app once
* `cd ..` : change directory back into the root
* `python3 manage.py runserver` : runs the server for testing

Navigate to `http://localhost:8000/` to see the application running.

> Note that the link `/static/` specified as STATIC_URL in `gitmate/settings.py` links the static serve of files, so all static links
> in `frontend/index.html` should prefix the same, and the `baseURL` settings
> of `frontend/system.config.js` should reflect the same, for proper functioning of the application.

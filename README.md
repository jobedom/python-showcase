# python-showcase

**Author**: Joaquín Bernal \
**email**: jobedom@gmail.com

This project is a coding exercise used in the past to show my coding style and
abilities. Feel free to ask any question regarding technical decisions.

---

## Overall project structure

The `src` folder contains the Python app.

The `src/tests` folder contains the tests.

## Architecture considerations

Three main responsibilities needed to be covered:

1. REST server for main application (FastAPI application `app` in module
   `main`)
2. Storage manager (`Storage` class in module `storage`)
3. Business rules for download limits (`DownloadRules` in module
   `download_rules`)

For this kind of exercise creating such a separation in several modules and
classes could appear as overkill, but in my opinion the concerns addressed in
each of those are well differentiated and different enough to justify such
separation.

In some future development, several kinds of storage could be needed, for
example. In such case, a refactor for the `Storage` class could end with a
`BaseStorage` abstract class and several implementations of derived classes
with different storage backends (database, file system, S3, etc.) Following the
YAGNI principle, I decided to implement the specific storage manager actually
needed in the exercise without creating extra complexity unneeded at the
moment.

There's a `settings` module for defining the required constants (business
related values, such as file count limit or download rate limits).

Such settings are read in the `main` module and the needed values are passed as
parameters in the instantiation of both the storage manager and the download
rules class. This allows the the settings handling centralization in the main
application iself and, also, allows a much cleaner unit testing for such pieces
of code (by means of just passing test values for those settings in the
instantiation inside the fixtures).

## Infrastructure

A `Makefile` is provided, including three targets: `build`, `test` and `run`.
Docker will be used to run things properly (tests or server) with independence
of your local environment.

The Python virtual environment for the development and execution of the
application and its tests is defined and maintained using pipenv. There are two
files, `Pipfile` and `Pipfile.lock`, which are used both during local
development and during the Docker build phase.

If you want to run or debug the server in your local environment, with the
proper pipenv setup, you can do:

```shell
pipenv run python -m uvicorn main:app --host 127.0.0.1  --port 9000
```

## How to run this

As explained above, there's a `Makefile` providing a few useful targets. In
order to run the tests:

```shell
make test
```

To launch the application server:

```shell
make run
```

This server will listen on port 9000.

## Specific endpoint details

The endpoint for saving a file (by a `POST` request to the URL `/files`)
expects the file itself under a multipart form  parameter named `file`.

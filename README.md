Koopera
=========

<img
  src="public/img/icon_blue.png"
  alt="Koopera"
  width="200"
/>

**Koopera** is a code review app for adding comments directly on `.ipynb` files

# Features
* Comment directly in jupyter notebook cells
* Github authentication via personal access token

# Screenshots

**Review jupyter notebooks**

<kbd><img title="Review jupyter notebooks" src="docs/add_comments_to_notebook.png"></kbd><br/>

**Review python code**

<kbd><img title="Review python code" src="docs/add_comments_to_python_file.png"></kbd><br/>

**Demo**

<kbd><img title="Demo" src="docs/demo.gif"></kbd><br/>


# Quickstart
You can easily start using Koopera with docker. You can get the image from [docker hub](https://hub.docker.com/r/rsn491/koopera) or build it from the source.

If you want to build, please run the cmd below:

`docker build -t koopera .`

To start the app, please run the cmd below:

`docker run -p 8080:8080 koopera`

The app can now be accessed at: [http://0.0.0.0:8080](http://0.0.0.0:8080)


# Setting up dev environment

## Dependencies
* Python 3.6
* nodejs 10

## Setting up backend for local development

1. Enable CORS by setting `ALLOW_CORS` to `True` in [src/backend/config.py](src/backend/config.py)

2. Create virtualenv

    `python -m venv venv`

3. Activate virtualenv

    `source venv/bin/activate`

4. Install dependencies

    `pip install -r requirements.txt`

5. Start flask app on default port (5000)

    `python run.py`

## Setting up frontend for local development

1. Install dependencies

    `npm install`
2. Run web server for serving frontend

    `npm run serve`

A web server for serving frontend with hot reload will be listening on
[http://localhost:8080](http://localhost:8080)

# Credits

<div>Icons made by <a href="https://www.flaticon.com/authors/nikita-golubev" title="Nikita Golubev">Nikita Golubev</a> from <a href="https://www.flaticon.com/"                 title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/"                 title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>

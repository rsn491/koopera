Koopera
=========

Koopera is a code review app that allows for adding comments to `.ipynb` files.

Note that this is a personal project that I initially started for playing with Vue.js and vanilla javascript.

# Features
* Add comments directly in notebooks cells
* Github authentication via personal access token

![demo](docs/demo.gif)

# Quickstart
You can easily start using Koopera with docker by running the
cmds below:


`$docker build -t koopera .`

`$docker run -p 8080:8080 koopera`
    
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
    
    `pip install -r requirements`

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

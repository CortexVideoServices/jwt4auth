`jwt4auth` library
==================

This repository contains a library that implements user session, authentication, and 
authorization. It is based on the use of the JWT `access_token` and `refresh_token`.

The access token is passed to the http only cookie by default, which should protect 
it from theft during a cross-site scripting attack.

The refresh token is passed in the body of the response on the `login` and `refresh` 
requests. It is stored in local storage. An update token can only be used with 
an access token, even if it has expired.

For more information, see the source code, which is enough documented and see the 
sample React application.

#### Currently available: 
* Server side for python aiohttp.
* Client side typescript client.
* Client side React components.


## How to start sample application
The best option is to download the repository and run the application in a virtual 
environment. To do this, run the following commands:

    git clone git@github.com:Alesh/jwt4auth.git
    cd jwt4auth
    python3.8 -m venv .venv
    source .venv/bin/activate
    pip install -U setuptools
    pip install -U pip
    pip install -U wheel
    pip install nodeenv
    nodeenv -p
    npm install yarn -g
    yarn install
    yarn build
    python setup.py develop
    python -m sample.backend
    
    

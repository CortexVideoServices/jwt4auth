`jwt4auth` library
==================

This repository contains a library that implements user session, authentication, 
and authorization. It is based on the use of the [JWT] access token and refreshes 
token.

The access token is passed to the HTTP the only cookie by default, which should 
protect it from theft during a cross-site scripting attack.

The refresh token is passed in the body of the response on the `login` and `refresh` 
requests. It is stored in local storage. The refresh token needs to update an access 
token.

#### Currently available: 
* [Server side Python module for aiohttp]
* [Typescript client library]
* [React component library]


#### How to start sample application and check it
The best way is to download the repository and run an application in a virtual 
environment. Run the following commands:

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
    python -m sample.backend --static-path sample/build
    
#### How to use that
There is a good example of a [React] based app frontend and [aiohttp] based backend. 
We hope the sample application helps you to get started using this set of libraries.
For more information, see the source code, which is enough documented

[JWT]: https://jwt.io/
[React]: https://https://reactjs.org/
[aiohttp]: https://docs.aiohttp.org/en/stable/

[Server side Python module for aiohttp]: https://pypi.org/project/jwt4auth/
[Typescript client library]: https://www.npmjs.com/package/@jwt4auth/general
[React component library]: https://www.npmjs.com/package/@jwt4auth/reactjs

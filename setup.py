from setuptools import setup, find_namespace_packages


def long_description():
    with open('README.md') as README_file:
        return README_file.read()


settings = {
    'name': 'jwt4auth',
    'author': 'Alexey Poryadin',
    'author_email': 'alexey.poryadin@gmail.com',
    'url': 'https://github.com/alesh/jwt4auth',
    'long_description': long_description(),
    'long_description_content_type': 'text/markdown',
    'keywords': 'jwt access refresh token auth authentication authorization aiohttp react typescript javascript',
    'license': 'http://opensource.org/licenses/LGPL-3.0',
    'classifiers': [
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
    ],
    'setup_requires': ['setuptools-vcs-version'],
    'version_config': {
        'version_style': {
            'metadata': False,
            'dirty': True,
        }
    },
    'zip_safe': False,
    'include_package_data': True,
    'packages': find_namespace_packages(exclude=['sample', 'sample.*', 'node_modules.*', 'packages.*']),
    'install_requires': [
        'aiohttp==3.7.2',
        'PyJWT==1.7.1'
    ]
}

setup(**settings)

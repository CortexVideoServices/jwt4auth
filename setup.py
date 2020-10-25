from setuptools import setup, find_namespace_packages

settings = {
    'name': 'jwt4auth',
    'author': 'Alexey Poryadin',
    'author_email': 'alexey.poryadin@gmail.com',
    'license': 'http://opensource.org/licenses/MIT',
    'setup_requires': ['setuptools-vcs-version'],
    'version_config': {
        'version_style': {
            'metadata': True,
            'dirty': True,
        }
    },
    'zip_safe': False,
    'packages': find_namespace_packages(),
    'install_requires': []
}

setup(**settings)

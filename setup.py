import os
from setuptools import setup, find_packages

fields = {}
with open(os.path.join('q2k', 'version.py')) as f:
    exec(f.read(), fields)
    __version__ = fields['Q2K_VERSION']

setup(
    name        = 'q2k',
    version     = __version__,
    description = 'Convert AVR C based QMK keymap and matrix files to YAML Keyplus format',
    url         = 'https://github.com/2Cas/Q2K',
    author      = '2Cas',
    author_email= '2Cas@seethis.link',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
    ],
    license = 'MIT',
    packages = find_packages(include=['q2k', 'q2k.*']),
    python_requires  = '>=3.5',
    install_requires = [
        'pyyaml', 'pyparsing', 'termcolor'
    ],
    entry_points = {
        'console_scripts': ['q2k-cli=q2k.core:q2keyplus', 'q2k=q2k.gui:main']
    },
    keywords = ['keyboard', 'usb', 'hid', 'qmk', 'keyplus'],
    zip_safe = False,
    include_package_data = True,
)

"""Copyright 2019 -

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import inspect
import os

from setuptools import setup, find_packages

# Import our own module here for version number
import cli

# Inspect to find current path
setup_path = inspect.getfile(inspect.currentframe())
setup_dir = os.path.dirname(setup_path)

# Find longer description from README
with open(os.path.join(setup_dir, "README.md"), "r") as fh:
    long_description = fh.read()


setup(
    name="radon-cli",
    version=cli.__version__,
    description="Radon Command Line Interface",
    packages=find_packages(),
    long_description=long_description,
    author="Jerome Fuselier",
    maintainer_email="",
    license="Apache License, Version 2.0",
    url="",
    setup_requires=["setuptools-git"],
    entry_points={"console_scripts": ["radon = cli.radon:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: System :: Archiving",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
    ],
)

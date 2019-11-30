
Radon Command Line Interface
=============================

Description
-----------

A Python client and command-line tool for the Radon data management system.
Includes a rudimentary client for any CDMI enabled cloud storage.

After Installation, connect to a Radon node::

    radon init --url=http://radon.example.com

(or if authentication is required by the archive)::

    radon init --url=http://radon.example.com --username=USER --password=PASS

(if you don't want to pass the password in the command line it will be asked if
you don't provide the --password option)
    radon init --url=http://radon.example.com --username=USER

Close the current session to prevent unauthorized access::

    radon exit

Show current working container::

    radon pwd

Show current authenticated user::

    radon whoami

List a container::

    radon ls <path>

List a container with ACL information::

    radon ls -a <path>

Move to a new container::

    radon cd <path>
    ...
    radon cd ..  # back up to parent

Create a new container::

    radon mkdir <path>

Put a local file, with eventually a new name::

    radon put <src>
    ...
    radon put <src> <dst>

Create a reference object::

    radon put --ref <url> <dest>

Provide the MIME type of the object (if not supplied ``radon put`` will attempt
to guess)::

     radon put --mimetype="text/plain" <src>

Fetch a data object from the archive to a local file::

    radon get <src>

    radon get <src> <dst>

    radon get --force <src> # Overwrite an existing local file

Get the CDMI json dict for an object or a container

    radon cdmi <path>

Remove an object or a container::

    radon rm <src>

Add or modify an ACL to an object or a container::

    radon chmod <path> (read|write|null) <group>


Advanced Use - Metadata
~~~~~~~~~~~~~~~~~~~~~~~

Set (overwrite) a metadata value for a field::

    radon meta set <path> "org.dublincore.creator" "S M Body"
    radon meta set . "org.dublincore.title" "My Collection"

Add another value to an existing metadata field::

    radon meta add <path> "org.dublincore.creator" "A N Other"

List metadata values for all fields::

    radon meta ls <path>

List metadata value(s) for a specific field::

    radon meta ls <path> org.dublincore.creator

Delete a metadata field::

    radon meta rm <path> "org.dublincore.creator"

Delete a specific metadata field with a value::

    radon meta rm <path> "org.dublincore.creator" "A N Other"


Advanced Use - Administration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List existing users::

    radon admin lu

List information about a user::

    radon admin lu <name>

List existing groups::

    radon admin lg

List information about a group::

    radon admin lg <name>

Create a user::

    radon admin mkuser [<name>]

Modify a user::

    radon admin moduser <name> (email | administrator | active | password) [<value>]

Remove a user::

    radon admin rmuser [<name>]

Create a group::

    radon admin mkgroup [<name>]

Remove a group::

    radon admin rmgroup [<name>]

Add user(s) to a group::

    radon admin atg <name> <user> ...

Remove user(s) from a group::

    radon admin rfg <name> <user> ...



Installation
------------

Create And Activate A Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ python3 -m venv ~/ve/radon-cli
    ...
    $ source ~/ve/radon-cli/bin/activate


Install Dependencies
~~~~~~~~~~~~~~~~~~~~
::

    pip install -r requirements.txt


Install Radon Client
~~~~~~~~~~~~~~~~~~~~
::

    pip install -e .


License
-------

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


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


class RadonClientError(Exception):
    """Base Class for Radon Command Line Interface Exceptions.

    Abstract Base Class from which more specific Exceptions are derived.
    """

    def __init__(self, code, msg):
        super(RadonClientError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return "Client Error {}: {}".format(self.code, self.msg)


class HTTPError(RadonClientError):
    """Radon HTTP Exception."""

    def __str__(self):
        return "HTTP Error {}: {}".format(self.code, self.msg)


class RadonConnectionError(RadonClientError):
    """Radon client connection Exception."""

    def __str__(self):
        return "Connection Error {}: {}".format(self.code, self.msg)


class NoSuchObjectError(RadonClientError):
    """Radon client no such object Exception."""

    def __str__(self):
        return "Object already exists at {0}".format(self.msg)


class ObjectConflictError(RadonClientError):
    """Radon object already exists Exception."""

    def __str__(self):
        return "Object already exists at {0}".format(self.msg)

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

__doc_opt__ = """
Radon Command Line Interface.

Usage:
  radon init --url=<URL> [--username=<USER>] [--password=<PWD>]
  radon whoami
  radon exit
  radon pwd
  radon ls [<path>] [-a]
  radon cd [<path>]
  radon cdmi <path>
  radon mkdir <path>
  radon put <src> [<dest>] [--mimetype=<MIME>]
  radon put --ref <url> <dest> [--mimetype=<MIME>]
  radon get <src> [<dest>] [--force]
  radon rm <path>
  radon chmod <path> (read|write|null) <group>
  radon meta add <path> <meta_name> <meta_value>
  radon meta set <path> <meta_name> <meta_value>
  radon meta rm <path> <meta_name> [<meta_value>]
  radon meta ls <path> [<meta_name>]
  radon admin lu [<name>]
  radon admin lg [<name>]
  radon admin mkuser [<name>]
  radon admin mkldapuser [<name>]
  radon admin moduser <name> (email | administrator | active | password) [<value>]
  radon admin rmuser [<name>]
  radon admin mkgroup [<name>]
  radon admin rmgroup [<name>]
  radon admin atg <name> <user> ...
  radon admin rfg <name> <user> ...
  radon (-h | --help)
  radon --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --url=<URL>   Location of Radon server


"""

import errno
import os
import pickle
import sys
from getpass import getpass
from operator import methodcaller
import json
import string
import random

import requests
import requests.exceptions
from blessings import Terminal
from docopt import docopt

import cli
from cli.acl import cdmi_str_to_str_acemask, str_to_cdmi_str_acemask
from cli.client import RadonClient

SESSION_PATH = os.path.join(os.path.expanduser("~/.radon"), "session.pickle")


def random_password(length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(letters) for i in range(length))


class RadonApplication():
    """Methods for the CLI"""

    def __init__(self, session_path):
        self.terminal = Terminal()
        self.session_path = session_path

    def admin_atg(self, args):
        """Add user(s) to a group."""
        client = self.get_client(args)
        groupname = args["<name>"]
        ls_user = args["<user>"]
        res = client.add_user_group(groupname, ls_user)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_lg(self, args):
        """List all groups or a specific group if the name is specified"""
        client = self.get_client(args)
        if args["<name>"]:
            name = args["<name>"]
        else:
            name = None
        if name:
            res = client.list_group(name)
            if not res.ok():
                self.print_error(res.msg())
                return res.code()
            group_info = res.json()
            members = ", ".join(group_info.get("members", []))
            print("{0.bold}Group name{0.normal}: {1}".format(
                self.terminal, group_info.get("name", name)
            ))
            print("{0.bold}Group id{0.normal}: {1}".format(
                self.terminal, group_info.get("uuid", "")
            ))
            print("{0.bold}Members{0.normal}: {1}".format(self.terminal, members))
        else:
            res = client.list_groups()
            if not res.ok():
                self.print_error(res.msg())
                return res.code()
            for groupname in res.msg():
                print(groupname)
        return 0

    def admin_lu(self, args):
        """List all users or a specific user if the name is specified"""
        client = self.get_client(args)
        if args["<name>"]:
            name = args["<name>"]
        else:
            name = None
        if name:
            res = client.list_user(name)
            if not res.ok():
                self.print_error(res.msg())
                return res.code()
            user_info = res.json()
            groups = ", ".join([el["name"] for el in user_info.get("groups", [])])
            print("{0.bold}User name{0.normal}: {1}".format(
                self.terminal, user_info.get("username", name)
            ))
            print("{0.bold}Email{0.normal}: {1}".format(
                self.terminal, user_info.get("email", "")
            ))
            print("{0.bold}User id{0.normal}: {1}".format(
                self.terminal, user_info.get("uuid", "")
            ))
            print("{0.bold}Administrator{0.normal}: {1}".format(
                self.terminal, user_info.get("administrator", False)
            ))
            print("{0.bold}Active{0.normal}: {1}".format(
                self.terminal, user_info.get("active", False)
            ))
            print("{0.bold}Groups{0.normal}: {1}".format(self.terminal, groups))
        else:
            res = client.list_users()
            if not res.ok():
                self.print_error(res.msg())
                return res.code()
            for username in res.msg():
                print(username)
        return 0

    def admin_mkgroup(self, args):
        """Create a new group. Ask in the terminal for mandatory fields"""
        client = self.get_client(args)
        if not args["<name>"]:
            groupname = input("Please enter the group name: ")
        else:
            groupname = args["<name>"]
        res = client.list_group(groupname)
        if res.ok():
            self.print_error("Groupname {} already exists".format(groupname))
            return 409  # Conflict
        res = client.create_group(groupname)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_mkuser(self, args):
        """Create a new user. Ask in the terminal for mandatory fields"""
        client = self.get_client(args)
        if not args["<name>"]:
            username = input("Please enter the user's username: ")
        else:
            username = args["<name>"]
        res = client.list_user(username)
        if res.ok():
            self.print_error("Username {} already exists".format(username))
            return 409  # Conflict
        admin = input("Is this an administrator? [y/N] ")
        email = ""
        while not email:
            email = input("Please enter the user's email address: ")
        password = ""
        while not password:
            password = getpass("Please enter the user's password: ")
        res = client.create_user(username, email, admin.lower() == "y", password)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_mkldapuser(self, args):
        """Create a new ldapuser. Ask in the terminal for mandatory fields
        the password of the ldap user is a fake one that isn't intended to be used
        email will be in ldap also"""
        client = self.get_client(args)
        if not args["<name>"]:
            username = input("Please enter the user's username: ")
        else:
            username = args["<name>"]
        res = client.list_user(username)
        if res.ok():
            self.print_error("Username {} already exists".format(username))
            return 409  # Conflict
        admin = input("Is this an administrator? [y/N] ")
        email = "user@ldap.com"
        # while not email:
        #    email = input("Please enter the user's email address: ")
        password = random_password(20)
        # while not password:
        #    password = getpass("Please enter the user's password: ")
        res = client.create_user(username, email, admin.lower() == "y", password)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_moduser(self, args):
        """Moduser a new user. Ask in the terminal if the value isn't
        provided"""
        client = self.get_client(args)
        value = args["<value>"]
        name = args["<name>"]
        if not value:
            if args["password"]:
                while not value:
                    value = getpass("Please enter the new password: ")
            else:
                while not value:
                    value = input("Please enter the new value: ")
                value = args["<value>"]
        user_dict = {}
        if args["email"]:
            user_dict["email"] = value
        elif args["administrator"]:
            user_dict["administrator"] = value.lower() in ["true", "y", "yes"]
        elif args["active"]:
            user_dict["active"] = value.lower() in ["true", "y", "yes"]
        elif args["password"]:
            user_dict["password"] = value
        res = client.mod_user(name, user_dict)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_rmgroup(self, args):
        """Remove a group."""
        client = self.get_client(args)
        if not args["<name>"]:
            groupname = input("Please enter the group name: ")
        else:
            groupname = args["<name>"]
        res = client.rm_group(groupname)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_rmuser(self, args):
        """Remove a user."""
        client = self.get_client(args)
        if not args["<name>"]:
            username = input("Please enter the user's username: ")
        else:
            username = args["<name>"]
        res = client.rm_user(username)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def admin_rfg(self, args):
        """Remove user(s) from a group."""
        client = self.get_client(args)
        groupname = args["<name>"]
        ls_user = args["<user>"]
        res = client.rm_user_group(groupname, ls_user)
        if res.ok():
            self.print_success(res.msg())
        else:
            self.print_error(res.msg())
            return res.code()
        return 0

    def change_dir(self, args):
        "Move into a different container."
        client = self.get_client(args)
        if args["<path>"]:
            path = args["<path>"]
        else:
            path = "/"
        res = client.chdir(path)
        if res.ok():
            # Save the client for future use
            self.save_client(client)
        else:
            self.print_error(res.msg())
        return 0

    def cdmi(self, args):
        "Display cdmi information (dict) for a path."
        client = self.get_client(args)
        path = args["<path>"]
        res = client.get_cdmi(path)
        if res.ok():
            print("{} :".format(client.normalize_cdmi_url(path)))
            path_json = res.json()
            for key, value in path_json.items():
                if key != "value":
                    print("  - {0.bold}{1}{0.normal}: {2}".format(
                        self.terminal, key, value
                    ))
        else:
            self.print_error(res.msg())

    def chmod(self, args):
        "Add or remove ACE to a path."
        client = self.get_client(args)
        path = args["<path>"]
        group = args["<group>"]
        if args["read"]:
            level = "read"
        elif args["write"]:
            level = "read/write"
        else:
            level = "null"
        ace = {
            "acetype": "ALLOW",
            "identifier": group,
            "aceflags": "CONTAINER_INHERIT, OBJECT_INHERIT",
            "acemask": str_to_cdmi_str_acemask(level, False),
        }
        metadata = {"cdmi_acl": [ace]}
        res = client.put(path, metadata=metadata)
        if res.ok():
            self.print_success(res.msg())
        else:
            if res.code() == 403:
                self.print_error(
                    "You don't have the rights to access ACL for this collection"
                )
            else:
                self.print_error(res.msg())
            return res.code()
        return 0

    def create_client(self, args):
        """Return a RadonClient."""
        url = args["--url"]
        if not url:
            # Called without being connected
            self.print_error("You need to be connected to access the server.")
            sys.exit(-1)
        client = RadonClient(url)
        # Test for client connection errors here
        res = client.get_cdmi("/")
        if res.code() in [0, 401, 403]:
            # 0 means success
            # 401/403 means authentication problem, we allow for authentication
            # to take place later
            return client
        else:
            self.print_error(res.msg())
            sys.exit(res.code())

    def exit(self):
        "Close CDMI client session"
        try:
            os.remove(self.session_path)
        except OSError:
            # No saved client to log out
            pass

    def get(self, args):
        "Fetch a data object from the archive to a local file."
        src = args["<src>"]
        # Determine local filename
        if args["<dest>"]:
            localpath = args["<dest>"]
        else:
            localpath = src.rsplit("/")[-1]

        # Check for overwrite of existing file, directory, link
        if os.path.isfile(localpath):
            if not args["--force"]:
                self.print_error(
                    "File '{0}' exists, --force option not used" "".format(localpath)
                )
                return errno.EEXIST
        elif os.path.isdir(localpath):
            self.print_error("'{0}' is a directory".format(localpath))
            return errno.EISDIR
        elif os.path.exists(localpath):
            self.print_error("'{0}'exists but not a file".format(localpath))
            return errno.EEXIST

        client = self.get_client(args)
        try:
            cfh = client.open(src)
            if cfh.status_code == 404:
                self.print_error("'{0}': No such object or container" "".format(src))
                return 404
        except requests.exceptions.ConnectionError as excpt:
            self.print_error(
                "'{0}': Redirection failed - Reference isn't accessible"
                "".format(excpt.request.url)
            )
            return 404
        lfh = open(localpath, "wb")
        for chunk in cfh.iter_content(8192):
            lfh.write(chunk)
        lfh.close()
        print(localpath)
        return 0

    def get_client(self, args):
        """Return a RadonClient.

        This may be achieved by loading a RadonClient with a previously saved
        session.
        """
        try:
            # Load existing session, so as to keep current dir etc.
            with open(self.session_path, "rb") as fhandle:
                client = pickle.load(fhandle)
        except (IOError, pickle.PickleError):
            # Init a new RadonClient
            client = self.create_client(args)
        
        if args["--url"]:
            if client.url != args["--url"]:
                # Init a fresh RadonClient
                client = self.create_client(args)
        client.session = requests.Session()
        return client

    def init(self, args):
        """Initialize a CDMI client session.

        Optionally log in using HTTP Basic username and password credentials.
        """
        client = self.get_client(args)
        if args["--username"]:
            username = args["--username"]
        else:
            username = None
        if args["--password"]:
            password = args["--password"]
        else:
            password = None
        if username:
            if not password:
                # Request password from interactive prompt
                password = getpass("Password: ")

            res = client.authenticate(username, password)
            if res.ok():
                print(
                    "{0.bold_green}Success{0.normal} - {1} as "
                    "{0.bold}{2}{0.normal}".format(self.terminal, res.msg(), username)
                )
            else:
                print("{0.bold_red}Failed{0.normal} - {1}".format(
                    self.terminal, res.msg()
                ))
                # Failed to log in
                # Exit without saving client
                return res.code()
        else:
            print(
                "{0.bold_green}Connected{0.normal} -"
                " Anonymous access".format(self.terminal)
            )
        # Save the client for future use
        self.save_client(client)
        return 0

    def ls(self, args):
        """List a container."""
        client = self.get_client(args)
        if args["<path>"]:
            path = args["<path>"]
        else:
            path = None
        res = client.ls(path)
        if res.ok():
            cdmi_info = res.json()
            pwd = client.pwd()
            if path is None:
                if pwd == "/":
                    print("Root:")
                else:
                    print("{}:".format(pwd))
            else:
                print("{}{}:".format(pwd, path))
            # Display Acl
            if args["-a"]:
                metadata = cdmi_info.get("metadata", {})
                cdmi_acl = metadata.get("cdmi_acl", [])
                if cdmi_acl:
                    for ace in cdmi_acl:
                        print("  ACL - {}: {}".format(
                            ace["identifier"],
                            cdmi_str_to_str_acemask(ace["acemask"], False),
                        ))
                else:
                    print("  ACL: No ACE defined")

            if cdmi_info["objectType"] == "application/cdmi-container":
                containers = [x for x in cdmi_info["children"] if x.endswith("/")]
                objects = [x for x in cdmi_info["children"] if not x.endswith("/")]
                for child in sorted(containers, key=methodcaller("lower")):
                    print(self.terminal.blue(child))
                for child in sorted(objects, key=methodcaller("lower")):
                    print(child)
            else:
                print(cdmi_info["objectName"])
            return 0
        else:
            self.print_error(res.msg())
            return res.code()

    def meta_add(self, args, replace=False):
        """Add metadata"""
        client = self.get_client(args)
        path = args["<path>"]
        meta_name = args["<meta_name>"]
        meta_value = args["<meta_value>"]
        if path in (".", "./"):
            path = client.pwd()
        res = client.get_cdmi(path)
        if not res.ok():
            self.print_error(res.msg())
            return res.code()
        cdmi_info = res.json()
        metadata = cdmi_info["metadata"]
        if meta_name in metadata:
            if replace:
                metadata[meta_name] = meta_value
            else:
                try:
                    # Already a list, we add it
                    metadata[meta_name].append(meta_value)
                except AttributeError:
                    # Only 1 element, we create a list
                    metadata[meta_name] = [metadata[meta_name], meta_value]
        else:
            metadata[meta_name] = meta_value
        res = client.put(path, metadata=metadata)
        if not res.ok():
            self.print_error(res.msg())
            return res.code()
        return 0

    def meta_ls(self, args):
        """List metadata"""
        client = self.get_client(args)
        path = args["<path>"]
        if args["<meta_name>"]:
            meta_name = args["<meta_name>"]
        else:
            meta_name = None
        if path in (".", "./"):
            path = client.pwd()
        res = client.get_cdmi(path)
        if not res.ok():
            self.print_error(res.msg())
            return res.code()
        cdmi_info = res.json()
        if meta_name:
            # List 1 field
            if meta_name in cdmi_info["metadata"]:
                print("{0}:{1}".format(meta_name, cdmi_info["metadata"][meta_name]))
        else:
            # List everything
            for attr, val in cdmi_info["metadata"].items():
                if attr.startswith(("cdmi_")):
                    # Ignore non-user defined metadata
                    continue
                if isinstance(val, list):
                    for v in val:
                        print("{0}:{1}".format(attr, v))
                else:
                    print("{0}:{1}".format(attr, val))
        return 0

    def meta_rm(self, args):
        """Remove metadata"""
        client = self.get_client(args)
        path = args["<path>"]
        meta_name = args["<meta_name>"]
        if args["<meta_value>"]:
            meta_value = args["<meta_value>"]
        else:
            meta_value = None
        if path in (".", "./"):
            path = client.pwd()
        res = client.get_cdmi(path)
        if not res.ok():
            self.print_error(res.msg())
            return res.code()
        cdmi_info = res.json()
        metadata = cdmi_info["metadata"]
        if meta_value:
            # Remove a specific value
            ex_val = metadata.get(meta_name, None)
            if isinstance(ex_val, list):
                # Remove all elements of the list with value val
                metadata[meta_name] = [x for x in ex_val if x != meta_value]
            elif ex_val == meta_value:
                # Remove a single element if that's the one we wanted to
                # remove
                del metadata[meta_name]
        else:
            try:
                del metadata[meta_name]
            except KeyError:
                # Metadata not defined
                pass
        res = client.put(path, metadata=metadata)
        if not res.ok():
            self.print_error(res.msg())
            return res.code()
        return 0

    def mkdir(self, args):
        "Create a new container."
        client = self.get_client(args)
        path = args["<path>"]
        if not path.startswith("/"):
            # relative path
            path = "{}{}".format(client.pwd(), path)
        res = client.mkdir(path)
        if not res.ok():
            self.print_error(res.msg())

    def print_error(self, msg):
        """Display an error message."""
        print("{0.bold_red}Error{0.normal} - {1}".format(self.terminal, msg))

    def print_success(self, msg):
        """Display a success message."""
        print("{0.bold_green}Success{0.normal} - {1}".format(self.terminal, msg))

    def print_warning(self, msg):
        """Display a warning message."""
        print("{0.bold_blue}Warning{0.normal} - {1}".format(self.terminal, msg))

    def put(self, args):
        "Put a file to a path."
        if args["--ref"]:
            return self.put_reference(args)
        src = args["<src>"]
        # Absolutize local path
        local_path = os.path.abspath(src)
        if args["<dest>"]:
            dest = args["<dest>"]
        else:
            # PUT to same name in pwd on server
            dest = os.path.basename(local_path)
        if not os.path.exists(local_path):
            self.print_error("File '{}' doesn't exist".format(local_path))
            return errno.ENOENT
        with open(local_path, "rb") as fh:
            client = self.get_client(args)
            # To avoid reading large files into memory,
            # client.put() accepts file-like objects
            res = client.put(dest, fh, mimetype=args["--mimetype"])
            if res.ok():
                cdmi_info = res.json()
                print(cdmi_info["parentURI"] + cdmi_info["objectName"])
            else:
                self.print_error(res.msg())
        return 0

    def put_reference(self, args):
        "Create a reference at path dest with the url."
        dest = args["<dest>"]
        url = args["<url>"]
        client = self.get_client(args)
        dict_data = {"reference": url}
        if args["--mimetype"]:
            dict_data["mimetype"] = args["--mimetype"]
        data = json.dumps(dict_data)
        res = client.put_cdmi(dest, data)
        if res.ok():
            cdmi_info = res.json()
            print(cdmi_info["parentURI"] + cdmi_info["objectName"])
        else:
            self.print_error(res.msg())

    def pwd(self, args):
        """Print working directory"""
        client = self.get_client(args)
        print(client.pwd())

    def rm(self, args):
        """Remove a data object or a collection.

        If we forget the trailing '/' for a collection we try to add it.
        """
        path = args["<path>"]
        client = self.get_client(args)
        res = client.delete(path)
        if res.code() == 404:
            # Possibly a container given without trailing
            # Try fetching in order to give correct response
            res = client.get_cdmi(path + "/")
            if not res.ok():
                # It really does not exist!
                self.print_error(
                    (
                        "Cannot remove '{0}': "
                        "No such object or container)"
                        "".format(path)
                    )
                )
                return 404
            cdmi_info = res.json()
            # Fixup path and recursively call this function (rm)
            args["<path>"] = "{}{}".format(
                cdmi_info["parentURI"], cdmi_info["objectName"]
            )
            return self.rm(args)
        return 0

    def save_client(self, client):
        """Save the status of the RadonClient for subsequent use."""
        if not os.path.exists(os.path.dirname(self.session_path)):
            os.makedirs(os.path.dirname(self.session_path))
        # Save existing session, so as to keep current dir etc.
        with open(self.session_path, "wb") as fh:
            pickle.dump(client, fh, pickle.HIGHEST_PROTOCOL)

    def whoami(self, args):
        """Print name of the user"""
        client = self.get_client(args)
        print(client.whoami() + " - " + client.url)


def main():
    """Main function"""
    arguments = docopt(__doc_opt__, version="Radon CLI {}".format(cli.__version__))
    app = RadonApplication(SESSION_PATH)

    if arguments["init"]:
        return app.init(arguments)

    elif arguments["meta"]:
        if arguments["add"]:
            return app.meta_add(arguments)
        elif arguments["set"]:
            return app.meta_add(arguments, True)
        elif arguments["ls"]:
            return app.meta_ls(arguments)
        elif arguments["rm"]:
            return app.meta_rm(arguments)

    elif arguments["admin"]:
        if arguments["lu"]:
            return app.admin_lu(arguments)
        if arguments["lg"]:
            return app.admin_lg(arguments)
        if arguments["mkuser"]:
            return app.admin_mkuser(arguments)
        if arguments["mkldapuser"]:
            return app.admin_mkldapuser(arguments)
        if arguments["moduser"]:
            return app.admin_moduser(arguments)
        if arguments["rmuser"]:
            return app.admin_rmuser(arguments)
        if arguments["mkgroup"]:
            return app.admin_mkgroup(arguments)
        if arguments["rmgroup"]:
            return app.admin_rmgroup(arguments)
        if arguments["atg"]:
            return app.admin_atg(arguments)
        if arguments["rfg"]:
            return app.admin_rfg(arguments)

    elif arguments["chmod"]:
        return app.chmod(arguments)
    elif arguments["exit"]:
        return app.exit()
    elif arguments["pwd"]:
        return app.pwd(arguments)
    elif arguments["ls"]:
        return app.ls(arguments)
    elif arguments["cd"]:
        return app.change_dir(arguments)
    elif arguments["cdmi"]:
        return app.cdmi(arguments)
    elif arguments["mkdir"]:
        return app.mkdir(arguments)
    elif arguments["put"]:
        return app.put(arguments)
    elif arguments["get"]:
        return app.get(arguments)
    elif arguments["rm"]:
        return app.rm(arguments)
    elif arguments["whoami"]:
        return app.whoami(arguments)

    return 0


if __name__ == "__main__":
    main()

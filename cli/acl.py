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


# aceflag: an int value taken from the constant ACEFLAG_*
# acemask:  an int value taken from the constant ACEMASK_*
# str: A simplified access level name (read, write, read/write or null)
# cdmi_str: A comma separated list of flags or masks, used in cdmi
#             ("READ_ACL, READ_ATTRIBUTES", ..)


# ACE Flags for ACL in CDMI
ACEFLAG_NONE = 0x00000000
ACEFLAG_OBJECT_INHERIT = 0x00000001
ACEFLAG_CONTAINER_INHERIT = 0x00000002
ACEFLAG_NO_PROPAGATE = 0x00000004
ACEFLAG_INHERIT_ONLY = 0x00000008
ACEFLAG_IDENTIFIER_GROUP = 0x00000040
ACEFLAG_INHERITED = 0x00000080

# ACE Mask bits for ACL in CDMI
ACEMASK_READ_OBJECT = 0x00000001
ACEMASK_LIST_CONTAINER = 0x00000001
ACEMASK_WRITE_OBJECT = 0x00000002
ACEMASK_ADD_OBJECT = 0x00000002
ACEMASK_APPEND_DATA = 0x00000004
ACEMASK_ADD_SUBCONTAINER = 0x00000004
ACEMASK_READ_METADATA = 0x00000008
ACEMASK_WRITE_METADATA = 0x00000010
ACEMASK_EXECUTE = 0x00000020
ACEMASK_DELETE_OBJECT = 0x00000040
ACEMASK_DELETE_SUBCONTAINER = 0x00000040
ACEMASK_READ_ATTRIBUTES = 0x00000080
ACEMASK_WRITE_ATTRIBUTES = 0x00000100
ACEMASK_WRITE_RETENTION = 0x00000200
ACEMASK_WRITE_RETENTION_HOLD = 0x00000400
ACEMASK_DELETE = 0x00010000
ACEMASK_READ_ACL = 0x00020000
ACEMASK_WRITE_ACL = 0x00040000
ACEMASK_WRITE_OWNER = 0x00080000
ACEMASK_SYNCHRONIZE = 0x00100000

# Ace flags table
ACEFLAG_TABLE = [
    (0x00000080, "INHERITED"),
    (0x00000040, "IDENTIFIER_GROUP"),
    (0x00000008, "INHERIT_ONLY"),
    (0x00000004, "NO_PROPAGATE"),
    (0x00000002, "CONTAINER_INHERIT"),
    (0x00000001, "OBJECT_INHERIT"),
    (0x00000000, "NO_FLAGS"),
]

# Ace masks table
ACEMASK_TABLE = [
    (0x00100000, "SYNCHRONIZE", "SYNCHRONIZE"),
    (0x00080000, "WRITE_OWNER", "WRITE_OWNER"),
    (0x00040000, "WRITE_ACL", "WRITE_ACL"),
    (0x00020000, "READ_ACL", "READ_ACL"),
    (0x00010000, "DELETE", "DELETE"),
    (0x00000400, "WRITE_RETENTION_HOLD", "WRITE_RETENTION_HOLD"),
    (0x00000200, "WRITE_RETENTION", "WRITE_RETENTION"),
    (0x00000100, "WRITE_ATTRIBUTES", "WRITE_ATTRIBUTES"),
    (0x00000080, "READ_ATTRIBUTES", "READ_ATTRIBUTES"),
    (0x00000040, "DELETE_OBJECT", "DELETE_SUBCONTAINER"),
    (0x00000020, "EXECUTE", "EXECUTE"),
    (0x00000010, "WRITE_METADATA", "WRITE_METADATA"),
    (0x00000008, "READ_METADATA", "READ_METADATA"),
    (0x00000004, "APPEND_DATA", "ADD_SUBCONTAINER"),
    (0x00000002, "WRITE_OBJECT", "ADD_OBJECT"),
    (0x00000001, "READ_OBJECT", "LIST_CONTAINER"),
]

ACEMASK_STR_INT_OBJ = {
    "none": 0x0,
    "read": ACEMASK_READ_OBJECT | ACEMASK_READ_METADATA,  # 0x09
    "write": 0x56,  # ACEMASK_WRITE_OBJECT | ACEMASK_APPEND_DATA |
    # ACEMASK_WRITE_METADATA | ACEMASK_DELETE_OBJECT,
    "read/write": 0x09 | 0x56,
    "edit": 0x56,
    "delete": ACEMASK_DELETE,
    "SYNCHRONIZE": 0x00100000,
    "WRITE_OWNER": 0x00080000,
    "WRITE_ACL": 0x00040000,
    "READ_ACL": 0x00020000,
    "DELETE": 0x00010000,
    "WRITE_RETENTION_HOLD": 0x00000400,
    "WRITE_RETENTION": 0x00000200,
    "WRITE_ATTRIBUTES": 0x00000100,
    "READ_ATTRIBUTES": 0x00000080,
    "DELETE_OBJECT": 0x00000040,
    "EXECUTE": 0x00000020,
    "WRITE_METADATA": 0x00000010,
    "READ_METADATA": 0x00000008,
    "APPEND_DATA": 0x00000004,
    "WRITE_OBJECT": 0x00000002,
    "READ_OBJECT": 0x00000001,
}

ACEMASK_INT_STR_OBJ = {
    0x0: "none",
    0x09: "read",
    0x56: "write",
    0x5F: "read/write",
}

ACEMASK_STR_INT_COL = {
    "none": 0x0,
    "read": ACEMASK_LIST_CONTAINER | ACEMASK_READ_METADATA,
    "write": 0x56,  # ACEMASK_ADD_OBJECT | ACEMASK_ADD_SUBCONTAINER |
    # ACEMASK_WRITE_METADATA | ACEMASK_DELETE_SUBCONTAINER,
    "edit": 0x56,
    "read/write": 0x09 | 0x56,
    "delete": (ACEMASK_DELETE | ACEMASK_DELETE_OBJECT | ACEMASK_DELETE_SUBCONTAINER),
    "SYNCHRONIZE": 0x00100000,
    "WRITE_OWNER": 0x00080000,
    "WRITE_ACL": 0x00040000,
    "READ_ACL": 0x00020000,
    "DELETE": 0x00010000,
    "WRITE_RETENTION_HOLD": 0x00000400,
    "WRITE_RETENTION": 0x00000200,
    "WRITE_ATTRIBUTES": 0x00000100,
    "READ_ATTRIBUTES": 0x00000080,
    "DELETE_SUBCONTAINER": 0x00000040,
    "EXECUTE": 0x00000020,
    "WRITE_METADATA": 0x00000010,
    "READ_METADATA": 0x00000008,
    "ADD_SUBCONTAINER": 0x00000004,
    "ADD_OBJECT": 0x00000002,
    "LIST_CONTAINER": 0x00000001,
}

ACEMASK_INT_STR_COL = {
    0x0: "none",
    0x09: "read",
    0x56: "write",
    0x5F: "read/write",
}

ACEFLAG_STR_INT = {
    "INHERITED": 0x00000080,
    "IDENTIFIER_GROUP": 0x00000040,
    "INHERIT_ONLY": 0x00000008,
    "NO_PROPAGATE": 0x00000004,
    "CONTAINER_INHERIT": 0x00000002,
    "OBJECT_INHERIT": 0x00000001,
    "NO_FLAGS": 0x00000000,
}


def aceflag_to_cdmi_str(num_value):
    """Return the string value for ACE flag value given

    Return the string value for the ACE flag value given. It returns a text
    expression simpler to understand.

    :param num_value: ACE flag numeric value
    :type num_value: integer
    :rtype: string
    """
    res = []
    for idx in range(len(ACEFLAG_TABLE)):
        if num_value == 0:
            return ", ".join(res)

        if num_value & ACEFLAG_TABLE[idx][0] == ACEFLAG_TABLE[idx][0]:
            res.append(ACEFLAG_TABLE[idx][1])
            num_value = num_value ^ ACEFLAG_TABLE[idx][0]
    return ", ".join(res)


def acemask_to_cdmi_str(num_value, is_object):
    """Return the string value for ACE mask value given.

    Return the string value for the ACE mask value given. It returns a
    text expression simpler to understand.

    :param num_value: ACE mask numeric value
    :type num_value: integer
    :param is_object: True if the ACE relates to an object, False for a c
    :type is_object: boolean
    :rtype: string
    """
    res = []
    for idx in range(len(ACEMASK_TABLE)):
        if num_value == 0:
            return ", ".join(res)

        if num_value & ACEMASK_TABLE[idx][0] == ACEMASK_TABLE[idx][0]:
            if is_object:
                res.append(ACEMASK_TABLE[idx][1])
            else:
                res.append(ACEMASK_TABLE[idx][2])
            num_value = num_value ^ ACEMASK_TABLE[idx][0]
    return ", ".join(res)


def acemask_to_str(acemask, is_object):
    """Return the simplified access level from an acemask"""
    if is_object:
        return ACEMASK_INT_STR_OBJ.get(acemask, "")
    else:
        return ACEMASK_INT_STR_COL.get(acemask, "")


def str_to_acemask(lvl, is_object):
    """Return the acemask from a simplified access level"""
    if is_object:
        return ACEMASK_STR_INT_OBJ.get(lvl, 0)
    else:
        return ACEMASK_STR_INT_COL.get(lvl, 0)


def cdmi_str_to_aceflag(cdmi_str):
    """Return the aceflag from a cdmi string"""
    aceflag = 0
    ls_flag = cdmi_str.split(",")
    for flag in ls_flag:
        flag = flag.strip().upper()
        aceflag |= ACEFLAG_STR_INT.get(flag, 0)
    return aceflag


def cdmi_str_to_acemask(cdmi_str, is_object):
    """Return the acemask from a cdmi string"""
    if is_object:
        map_dict = ACEMASK_STR_INT_OBJ
    else:
        map_dict = ACEMASK_STR_INT_COL
    acemask = 0
    ls_mask = cdmi_str.split(",")
    for mask in ls_mask:
        mask = mask.strip().upper()
        acemask |= map_dict.get(mask, 0)
    return acemask


def cdmi_str_to_str_acemask(cdmi_str, is_object):
    """Return the simplified access level from a cdmi string"""
    acemask = cdmi_str_to_acemask(cdmi_str, is_object)
    return acemask_to_str(acemask, is_object)


def str_to_cdmi_str_acemask(lvl, is_object):
    """Return the cdmi string from a simplified access level"""
    acemask = str_to_acemask(lvl, is_object)
    return acemask_to_cdmi_str(acemask, is_object)

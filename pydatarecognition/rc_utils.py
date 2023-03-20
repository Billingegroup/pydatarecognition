"""
Necessary util functions to run runcontrol copied from regolith
"""

import os

from getpass import getpass

string_types = (str, bytes)
_FALSES = frozenset(["", "0", "n", "f", "no", "none", "false"])


def noop(x):
    """Does nothing, just returns the input."""
    return x


def is_int(x):
    """Tests if something is an integer"""
    return isinstance(x, int)


def always_true(x):
    """Returns True"""
    return True


def always_false(x):
    """Returns False"""
    return False


def is_bool(x):
    """Tests if something is a boolean"""
    return isinstance(x, bool)


def is_string(x):
    """Tests if something is a string"""
    return isinstance(x, string_types)


def to_bool(x):
    """"Converts to a boolean in a semantically meaningful way."""
    if isinstance(x, bool):
        return x
    elif isinstance(x, string_types):
        return False if x.lower() in _FALSES else True
    else:
        return bool(x)


def ensure_string(x):
    """Returns a string if x is not a string, and x if it already is."""
    if isinstance(x, string_types):
        return x
    else:
        return str(x)


def ensure_database(db):
    db["name"] = ensure_string(db["name"])
    db["url"] = ensure_string(db["url"])
    db["path"] = ensure_string(db["path"])
    db["public"] = to_bool(db.get("public", True))
    return db


def ensure_databases(dbs):
    """Ensures each dataset in a list of databases"""
    return list(map(ensure_database, dbs))


def ensure_store(store):
    store["name"] = ensure_string(store["name"])
    store["url"] = ensure_string(store["url"])
    store["path"] = ensure_string(store.get("path", None) or "")
    store["public"] = to_bool(store.get("public", True))
    return store


def ensure_stores(stores):
    """Ensures each store in a list of stores"""
    return list(map(ensure_store, stores))


def ensure_email(email):
    """Ensures the email top-level key is well-formed."""
    email["url"] = ensure_string(email["url"])
    if "cred" in email:
        email["cred"] = ensure_string(email["cred"])
    else:
        email["cred"] = email["url"] + ".cred"
    if not os.path.isfile(email["cred"]):
        user = input("Email address for " + email["url"] + ": ")
        password = getpass()
        s = user + "\n" + password
        with open(email["cred"], "w") as f:
            f.write(s)
    with open(email["cred"], encoding='utf-8') as f:
        email["from"] = f.readline().strip()
        email["password"] = f.readline().strip()
    email["user"] = email["from"].partition("@")[0]
    email["port"] = int(email.get("port", 0))
    email["verbosity"] = int(email.get("verbosity", 0))
    email["tls"] = to_bool(email.get("tls", False))
    return email


def dbdirname(db, rc):
    """Gets the database dir name."""
    if db.get("local", False) is False:
        dbsdir = os.path.join(rc.builddir, "_dbs")
        dbdir = os.path.join(dbsdir, db["name"])
    else:
        dbdir = db["url"]
    return dbdir


def dbpathname(db, rc):
    """Gets the database path name."""
    dbdir = dbdirname(db, rc)
    dbpath = os.path.join(dbdir, db["path"])
    return dbpath


def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup if
    cond is false. """

    def dec(obj):
        return obj if cond else backup

    return dec

"""Helps manage mongodb setup and connections."""
import os
from contextlib import contextmanager
from warnings import warn

from client_manager import ClientManager


def load_local_database(db, client, rc):
    """Loads a local database"""
    # make sure that we expand user stuff
    db['url'] = os.path.expanduser(db['url'])
    # import all of the data
    client.load_database(db)


def load_mpc_database(db, client):
    """Load a mpc database."""
    client.load_database(db)


def load_database(db, client, rc):
    """Loads a database"""
    if db['backend'] in ('mpc', 'mpcontribs'):
        load_mpc_database(db, client)
        return

    url = db['url']
    if os.path.exists(os.path.expanduser(url)):
        load_local_database(db, client, rc)
    else:
        raise ValueError('Do not know how to load this kind of database: '
                         '{}'.format(db))


def dump_local_database(db, client, rc):
    """Dumps a local database"""
    # dump all of the data
    client.dump_database(db)
    return


def dump_database(db, client, rc):
    """Dumps a database"""
    # do not dump mpc db
    if db['backend'] in ('mpc', 'mpcontribs'):
        return

    url = db['url']
    if os.path.exists(url):
        dump_local_database(db, client, rc)
    else:
        raise ValueError('Do not know how to dump this kind of database')


def open_dbs(rc, dbs=None):
    """Open the databases

    Parameters
    ----------
    rc : RunControl instance
        The rc which has links to the dbs
    dbs: set or None, optional
        The databases to load. If None load all, defaults to None

    Returns
    -------
    client : {FileSystemClient, MPCClient}
        The database client
    """
    if dbs is None:
        dbs = []
    client = ClientManager(rc.databases, rc)
    client.open()
    chained_db = {}
    for db in rc.databases:
        # if we only want to access some dbs and this db is not in that some
        db['whitelist'] = dbs
        if 'blacklist' not in db:
            db['blacklist'] = ['.travis.yml', '.travis.yaml']
        load_database(db, client, rc)

        # TODO: Delete ChainDB related code
        for base, coll in client.dbs[db['name']].items():
            if base not in chained_db:
                chained_db[base] = {}
            for k, v in coll.items():
                if k in chained_db[base]:
                    chained_db[base][k].maps.append(v)
                else:
                    chained_db[base][k] = ChainDB(v)
    client.chained_db = chained_db
    return client


@contextmanager
def connect(rc, dbs=None):
    """Context manager for ensuring that database is properly setup and torn
    down"""
    client = open_dbs(rc, dbs=dbs)
    yield client
    for db in rc.databases:
        dump_database(db, client, rc)
    client.close()

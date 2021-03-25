from sqlalchemy import create_engine
import yaml
import logging
log = logging.getLogger(__name__)
import sys, os
path = os.path.dirname(os.path.abspath(__file__))

def get_database():
    try:
        engine = get_connection_from_profile()
        log.info("Connected to PostgreSQL database!")
    except IOError:
        log.exception("Failed to get database connection!")
        return None, 'fail'
    return engine


def get_connection_from_profile(config_file_name="setup_psql_environment.yaml"):
    """
    Sets up database connection from config file.
    Input:
    config_file_name: File containing PGHOST, PGUSER,
                        PGPASSWORD, PGDATABASE, PGPORT, which are the
                        credentials for the PostgreSQL database
    """
    with open(path+'/'+config_file_name, 'r') as f:
        vals = yaml.safe_load(f)
    if not ('PGHOST' in vals.keys() and
            'PGUSER' in vals.keys() and
            'PGPASSWORD' in vals.keys() and
            'PGDATABASE' in vals.keys() and
            'PGPORT' in vals.keys()):
        raise Exception('Bad config file: ' + config_file_name)
    return get_engine(vals['PGDATABASE'], vals['PGUSER'],
                        vals['PGHOST'], vals['PGPORT'],
                        vals['PGPASSWORD'])


def get_engine(db, user, host, port, passwd):
    """
    Get SQLalchemy engine using credentials.
    Input:
    db: database name
    user: Username
    host: Hostname of the database server
    port: Port number
    passwd: Password for the database
    """
    url = 'postgresql://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=user, passwd=passwd, host=host, port=port, db=db)
    engine = create_engine(url, pool_size = 50, echo=False)
    return engine

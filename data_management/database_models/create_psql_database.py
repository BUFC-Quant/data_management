from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from setup_psql_environment import get_database
from sqlalchemy.ext.declarative import declarative_base

import models

db = get_database()
Session = sessionmaker(bind=db)
meta = MetaData(bind=db)
session = Session()

# Setup environment and create a session
if __name__ == '__main__':

    # Create database from SQLAlchemy models
    models.Base.metadata.create_all(db)
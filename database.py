from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# read URL for connection to database from config file
with open('db.config', 'r', encoding='utf8') as f:
    args = [row for row in f.read().split('\n')]
    args[3] = int(args[3])


url = 'postgresql://{}:{}@{}:{}/{}'.format(*args)
con = create_engine(url, client_encoding='utf8', echo=False)

Session = sessionmaker(bind=con)
session = Session()

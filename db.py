from sqlalchemy import create_engine
from models import Base

with open('db.config', 'r', encoding='utf8') as f:
    args = [row for row in f.read().split('\n')]
    args[3] = int(args[3])

url = 'postgresql://{}:{}@{}:{}/{}'.format(*args)
con = create_engine(url, client_encoding='utf8', echo=False)

# Base.metadata.create_all(con)  # создать таблицы
# Base.metadata.drop_all(con)  # удалить таблицы




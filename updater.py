import xml.etree.cElementTree as ET
from datetime import datetime
from io import StringIO

import pandas as pd
import requests as r

from database import con
from logger import logger

# ссылки на XML файлы
links = [
    'https://afmrk.gov.kz/blacklist/export/active/xml',
    'https://afmrk.gov.kz/blacklist/export/excluded/xml'
]


class Updater:
    def __init__(self, _links):
        self.links = _links  # ссылки на скачивание файлов
        self.person_cols = ('num', 'lname', 'fname', 'mname', 'birthdate', 'iin', 'note', 'correction')
        self.org_cols = ('num', 'org_name', 'org_name_en', 'note')
        self.tags = ('person', 'org')  # тэги для парсинга XML
        # для датафрэймов
        self.persons_df = None
        self.orgs_df = None
        self.history = None
        # последняя дата обновления бд
        with open('last_update.txt', 'r', encoding='utf8') as f:
            t = f.readline()
        self.last_update = t if len(t) > 0 else 'Неизвестно'  # тупой метод (:

    @staticmethod
    def download(link):  # скачивает файл по ссылке
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/91.0.4472.114 Safari/537.36 '}
        raw_data = r.get(link, headers=headers)  # скачиваем по ссылке данные
        data = StringIO()  # храним данные в ОЗУ
        data.write(raw_data.content.decode())  # записываем скачанную декодированную строку
        return ET.fromstring(data.getvalue())  # возвращаем XML элемент

    @staticmethod
    def xml2dict(xml_file, tag):  # данные из XML в словарь построчно, генерирует словарь
        for row in xml_file.iter(tag):
            dct = {}
            for col in row:
                dct.update({col.tag: col.text})
            yield dct

    def gen_df(self, file, tag, cols):  # создает датафрэйм из XML элемента
        return pd.DataFrame((list(self.xml2dict(file, tag))), columns=cols)

    def create_list_df(self, files, tags, cols):  # создает список с датафрэймами
        # idx = 0 - persons
        # idx = 1 - orgs
        persons = [self.gen_df(file, tags[0], cols[0]) for file in files]
        orgs = [self.gen_df(file, tags[1], cols[1]) for file in files]
        dataframes = persons + orgs
        return dataframes

    @staticmethod
    def prepare_df(dataframes):  # удаляем столбец num и добавляем столбец 'status' - active or exclude
        for i in range(len(dataframes)):
            dataframes[i] = dataframes[i].drop(columns=['num'], axis=1)
            if i % 2 == 0:  # нечетные датафрэйма - действующие, четные - исключенные
                dataframes[i]['status'] = ['active'] * len(dataframes[i])
            else:
                dataframes[i]['status'] = ['excluded'] * len(dataframes[i])

    def concat_df(self, dataframes):  # соединяем фрэймы в группы (лица, организации)
        # датафрэйм со всеми лицами
        self.persons_df = pd.concat([dataframes[i] for i in range(len(dataframes)) if i in (0, 1)],
                                    sort=False, ignore_index=True)

        # датафрэйм со всеми орг-ми
        self.orgs_df = pd.concat([dataframes[i] for i in range(len(dataframes)) if i in (2, 3)],
                                 sort=False, ignore_index=True)
        # индексирование с 1
        self.persons_df.index += 1
        self.orgs_df.index += 1

    def make_history(self):  # при обновлении бд, создает датафрэйм с историей
        history = pd.DataFrame(columns=['table', 'obj_id', 'note', 'date'])
        for i in range(len(self.persons_df)):
            history.loc[i] = ['persons', i + 1, 'Database update', self.last_update]
        for i in range(len(self.orgs_df)):
            history.loc[len(self.persons_df) + i] = ['organizations', i + 1, 'Database update', self.last_update]
        self.history = history

    @staticmethod
    def put_to_db(dataframe, connection, tablemame, chunksize, if_exists):
        dataframe.to_sql(con=connection, name=tablemame, if_exists=if_exists, chunksize=chunksize)
        logger.info('Table "{}" is fully updated'.format(tablemame))

    def update_status(self):
        with open('last_update.txt', 'w') as f:
            f.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        with open('last_update.txt', 'r', encoding='utf8') as f:
            t = f.readline()
        self.last_update = t

    def run(self):
        # список с XML файлами
        parsed_xml_files = [self.download(link) for link in self.links]
        # датафрэймы из пропарсенных XML файлов
        dataframes = self.create_list_df(parsed_xml_files, self.tags, (self.person_cols, self.org_cols))
        # удаление столбца num и добавления статуса active or excluded
        self.prepare_df(dataframes)
        # собираем вместе лица и организации
        self.concat_df(dataframes)
        # добавляем в лица и организацю базу
        self.put_to_db(dataframe=self.persons_df, connection=con, tablemame='persons',
                       if_exists='replace', chunksize=3000)
        self.put_to_db(dataframe=self.orgs_df, connection=con, tablemame='organizations', if_exists='replace',
                       chunksize=3000)
        # последняя дата обновления бд
        self.update_status()
        # история изменений
        self.make_history()
        # добавляем историю в базу
        self.put_to_db(self.history, connection=con, tablemame='history', if_exists='replace', chunksize=3000)
        logger.info('Database updated')

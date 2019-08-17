import requests as r
import xml.etree.cElementTree as ET
from io import StringIO
import pandas as pd
from database import con

# ссылки на XML файлы
links = ('https://kfm.gov.kz/blacklist/export/active/xml', 'https://kfm.gov.kz/blacklist/export/excluded/xml')


class Updater:
    def __init__(self, links):
        self.links = links  # ссылки на скачивание файлов
        self.person_cols = ('num', 'lname', 'fname', 'mname', 'birthdate', 'iin', 'note', 'correction')
        self.org_cols = ('num', 'org_name', 'org_name_en', 'note')
        self.tags = ('person', 'org')  # тэги для парсинга XML
        # для датафрэймов
        self.persons_df = None
        self.orgs_df = None

    @staticmethod
    def download(link):  # скачивает файл по ссылке
        raw_data = r.get(link)  # скачиваем по ссылке данные
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
    def prepare_df(dataframes): # удаляем столбец num и добавляем столбец 'status' - active or exclude
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

    @staticmethod
    def put_to_db(dataframe, connection, tablemame, chunksize):
        dataframe.to_sql(con=connection, name=tablemame, if_exists='replace', chunksize=chunksize)

    def run(self):
        # список с XML файлами
        parsed_xml_files = [self.download(link) for link in self.links]
        # датафрэймы из пропарсенных XML файлов
        dataframes = self.create_list_df(parsed_xml_files, self.tags, (self.person_cols, self.org_cols))
        # удаление столбца num и добавления статуса active or excluded
        self.prepare_df(dataframes)
        # собираем вместе лица и организации
        self.concat_df(dataframes)
        # добавляем в базу
        self.put_to_db(dataframe=self.persons_df, connection=con, tablemame='Persons', chunksize=3000)
        self.put_to_db(dataframe=self.orgs_df, connection=con, tablemame='Organizations', chunksize=3000)


upd = Updater(links)
upd.run()


import requests as r
import xml.etree.cElementTree as ET
from io import StringIO
import pandas as pd
from db import con

# ссылки на XML файлы
links = ('https://kfm.gov.kz/blacklist/export/active/xml', 'https://kfm.gov.kz/blacklist/export/excluded/xml')

# столбцы для DataFrame-ов
person_cols = ('num', 'lname', 'fname', 'mname', 'birthdate', 'iin', 'note', 'correction')
org_cols = ('num', 'org_name', 'org_name_en', 'note')

# для парсинга XML
tags = ('person', 'org')


def download(link):  # скачивает файл по ссылке
    raw_data = r.get(link)  # скачиваем по ссылке данные
    data = StringIO()  # храним данные в ОЗУ
    data.write(raw_data.content.decode())  # записываем скачанную декодированную строку
    return ET.fromstring(data.getvalue())  # возвращаем XML элемент


def xml2dict(xml_file, tag):  # данные из XML в словарь построчно, генерирует словарь
    for row in xml_file.iter(tag):
        dct = {}
        for col in row:
            dct.update({col.tag: col.text})
        yield dct


def gen_df(ctgr, tag, cols):  # создает датафрэйм из XML элемента
    return pd.DataFrame((list(xml2dict(ctgr, tag))), columns=cols)


parsed_xml_files = [download(link) for link in links]  # создаем список с XML элементами
active_xml = parsed_xml_files[0]  # ACTIVE persons and orgs
excluded_xml = parsed_xml_files[1]  # EXCLUDED persons and orgs

# for loop needed or generator
actv_persons = gen_df(active_xml, tags[0], person_cols)  # idx = 0
actv_orgs = gen_df(active_xml, tags[1], org_cols)  # idx = 1
actv_orgs_cis = gen_df(active_xml, tags[1], org_cols)  # idx = 2

ex_persons = gen_df(excluded_xml, tags[0], person_cols)  # idx = 3
ex_orgs = gen_df(excluded_xml, tags[1], org_cols)  # idx = 4
ex_orgs_cis = gen_df(excluded_xml, tags[1], org_cols)  # idx = 5

# list with all df
dataframes = [actv_persons, actv_orgs, actv_orgs_cis, ex_persons, ex_orgs, ex_orgs_cis]

for i in range(len(dataframes)):  # удаляем столбец num и добавляем столбец 'status' - active or excluded
    dataframes[i] = dataframes[i].drop(columns=['num'], axis=1)
    if i < 3:  # первые три датафрэйма - действующие, остальные - исключенные
        dataframes[i]['status'] = ['active'] * len(dataframes[i])
    else:
        dataframes[i]['status'] = ['excluded'] * len(dataframes[i])

# соединяем фрэймы в группы (лица, организации)
persons_df = pd.concat([dataframes[i] for i in range(len(dataframes)) if i in (0, 3)],  # датафрэйм со всеми лицами
                       sort=False, ignore_index=True)

orgs_df = pd.concat([dataframes[i] for i in range(len(dataframes)) if i in (1, 2, 4, 5)],  # датафрэйм со всеми орг-ми
                    sort=False, ignore_index=True)

# запись в бд
persons_df.to_sql(con=con, name='Persons', if_exists='replace', chunksize=3000)
orgs_df.to_sql(con=con, name='Organizations', if_exists='replace', chunksize=3000)

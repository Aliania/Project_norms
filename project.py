# %% md

В
данной
работе
я
решила
реализовать
мини - проект, который
бы
позволил
мне
автоматизировать
одну
из
рутинных
операций - расчет
норм
по
питанию.В
процессе
расчета
необходимо
перевести
массу
съеденного
продукта
из
брутто
в
нетто, а
так
же
сгруппировать
их
по
определенным
категориям.

# %%

import pandas as pd
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, "russian")

# %% md

Импортируем
файл
и
настроим
его
вывод

# %%

df = pd.read_excel('Norms.xlsx', )
month = df.loc[2, 'Unnamed: 0'].split()[2]
month_number = datetime.strptime(month, '%B').month
df = df.iloc[9:63]

data = df.drop(
    columns=['Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 8', 'Unnamed: 10',
             'Unnamed: 12'])  # Убираем лишние стоблцы
data = data.set_axis(
    ['product_name', 'weight_children', 'children_cost', 'nursery_weight', 'nursery_cost', 'weight_total',
     'cost_total'], axis='columns')  # Переименовываем столбцы
data = data.fillna('0')

# %% md

Создадим
таблицу
с
коэффициентами
перевода
в
нетто.

# %%

product_names_and_coeff = {'Вафли': 1,
                           'Геркулес': 1,
                           'Горох': 1,
                           'Дрожжи': 1,
                           'Зеленый горошек 0,420': 0.67,
                           'Зеленый горошек': 0.67,
                           'Изюм': 1,
                           'Какао': 1,
                           'Капуста': 0.8,
                           'Картофель': 0.6,
                           'Кефир': 1,
                           'Кисель сухой': 1,
                           'Кислота аскорбиновая': 1,
                           'Компот (сухофрукты)': 1,
                           'Кофе': 1,
                           'Крупа гречневая': 1,
                           'Крупа кукурузная': 1,
                           'Крупа манная': 1,
                           'Крупа перловая': 1,
                           'Крупа ячневая': 1,
                           'Лук': 0.84,
                           'Макаронные изделия': 1,
                           'Макаронные изделия "Вермишель"': 1,
                           'Масло растительное': 1,
                           'Масло сливочное': 1,
                           'Минтай': 0.58,
                           'Молоко свежее': 1,
                           'Молоко сухое цельное': 8.33,
                           'Морковь': 0.75,
                           'Мука пшеничная': 1,
                           'Мясо ЦБ': 0.66,
                           'Огурцы': 0.93,
                           'Огурцы консервированные 0,72': 0.6,
                           'Окорок свиной б/к': 0.852,
                           'Печень говяжья': 0.83,
                           'Печенье': 1,
                           'Повидло разное': 1,
                           'Помидоры': 0.85,
                           'Пшено': 1,
                           'Рис': 1,
                           'Ряженка': 1,
                           'Сахар песок': 1,
                           'Сода': 1,
                           'Свекла': 0.75,
                           'Сметана': 1,
                           'Сок фруктовый': 1,
                           'Сок фруктовый 0,2 для яслей': 1,
                           'Соль': 1,
                           'Сыр': 0.97,
                           'Творог': 0.985,
                           'Хлеб "Новый"': 1,
                           'Хлеб "Пшеничный"': 1,
                           'Хлеб "Ржаной"': 1,
                           'Чай': 1,
                           'Шиповник': 1,
                           'Яблоки': 0.88,
                           'Яйцо': 1}

if month_number >= 1 and month_number <= 8:
    product_names_and_coeff['Морковь'] = 0.75
else:
    product_names_and_coeff['Морковь'] = 0.8

if month_number >= 1 and month_number <= 8:
    product_names_and_coeff['Свекла'] = 0.75
else:
    product_names_and_coeff['Свекла'] = 0.8

if month_number >= 1 and month_number <= 2:
    product_names_and_coeff['Картофель'] = 0.65
elif month_number >= 3 and month_number <= 8:
    product_names_and_coeff['Картофель'] = 0.6
elif month_number >= 9 and month_number <= 10:
    product_names_and_coeff['Картофель'] = 0.75
elif month_number >= 11 and month_number <= 12:
    product_names_and_coeff['Картофель'] = 0.7

table_with_coeff = pd.DataFrame.from_dict(product_names_and_coeff, orient='index')
table_with_coeff.set_axis(['coefficient'], axis='columns', inplace=True)
table_with_coeff.index_name = 'product_name'
table_with_coeff['product_name'] = table_with_coeff.index
table_with_coeff = table_with_coeff.reset_index(drop=True)

# %% md

Соединяем
таблицы, добавляем
столбцы
с
расчетом
значений
в
нетто.

# %%

data_new = pd.merge(data, table_with_coeff, how='left', on='product_name')
data_new[['weight_children', 'nursery_weight']] = data_new[['weight_children', 'nursery_weight']].apply(pd.to_numeric,
                                                                                                        errors='coerce')
data_new.fillna('0')

data_new['weight_children_netto'] = data_new['weight_children'] * data_new['coefficient']
data_new['nursery_weight_netto'] = data_new['nursery_weight'] * data_new['coefficient']

# %% md

Сейчас
будем
группировать
значения
по
категориям.


# %%

def extract_children_weight(data, product_name):
    # data - используемый DataFrame
    # product_name - название продукта, данные по которому извлекаются
    name = str(product_name)
    product_value_series = data.loc[data['product_name'] == name]['weight_children_netto'].reset_index()
    if len(product_value_series) > 0:
        return product_value_series['weight_children_netto'][0]
    else:
        return 0


def extract_nursery_weight(data, product_name):
    # data - используемый DataFrame
    # product_name - название продукта, данные по которому извлекаются
    name = str(product_name)
    product_value_series = data.loc[data['product_name'] == name]['nursery_weight_netto'].reset_index()
    if len(product_value_series) > 0:
        return product_value_series['nursery_weight_netto'][0]
    else:
        return 0


def sum_of_extracts(data, names, category):
    # data - датафрейм с данными
    # names - список с названиями продуктов
    # category - название категории довольствующихся
    # Сама функция суммирует все значения по указанной категории продуктов в категории довольствующихся
    total = 0
    category = str(category)
    for name in names:
        if category == 'children':
            extract = extract_children_weight(data, name)
            total += extract
        elif category == 'nursery':
            extract = extract_nursery_weight(data, name)
            total += extract
        else:
            print('Введите верную категорию')
    return total


milk = ['Молоко свежее', "Молоко сухое цельное", "Кефир", "Ряженка"]
milk_production_children = sum_of_extracts(data_new, milk, 'children')
milk_production_nursery = sum_of_extracts(data_new, milk, 'nursery')

porridge = ['Геркулес', "Горох", "Крупа гречневая", "Крупа кукурузная", "Крупа манная", "Крупа перловая",
            "Крупа ячневая", "Пшено", "Рис"]
porridge_children = sum_of_extracts(data_new, porridge, 'children')
porridge_nursery = sum_of_extracts(data_new, porridge, 'nursery')

confectionary = ['Вафли', 'Печенье', 'Повидло разное']
confectionary_children = sum_of_extracts(data_new, confectionary, 'children')
confectionary_nursery = sum_of_extracts(data_new, confectionary, 'nursery')

vegetables = ['Зеленый горошек 0,420', 'Капуста', 'Лук', 'Морковь', 'Огурцы', 'Огурцы консервированные 0,72',
              'Помидоры', 'Зеленый горошек 0,420', 'Свекла']
vegetables_children = sum_of_extracts(data_new, vegetables, 'children')
vegetables_nursery = sum_of_extracts(data_new, vegetables, 'nursery')

dried_fruits = ['Компот (сухофрукты)', 'Изюм', 'Шиповник']
dried_fruits_children = sum_of_extracts(data_new, dried_fruits, 'children')
dried_fruits_nursery = sum_of_extracts(data_new, dried_fruits, 'nursery')

categories = ['мясо', 'птица', 'субпродукты', 'рыба', 'масло сливочное', 'масло растительное',
              'молоко и кисломолочные продукты', 'творог', 'сметана', 'сыр', 'яйцо (шт)', 'мука', 'крупы,бобовые',
              'макароны',
              'сахар', 'конд. изд.', 'с/фрукты', 'фрукты', 'соки', 'картофель', 'овощи', 'хлеб ржаной',
              'хлеб пшеничный или зерновой']

nursery_weight = [extract_nursery_weight(data_new, 'Окорок свиной б/к'), extract_nursery_weight(data_new, 'Мясо ЦБ'),
                  extract_nursery_weight(data_new, 'Печень говяжья'), extract_nursery_weight(data_new, 'Минтай'),
                  extract_nursery_weight(data_new, 'Масло сливочное'),
                  extract_nursery_weight(data_new, 'Масло растительное'), milk_production_nursery,
                  extract_nursery_weight(data_new, 'Творог'), extract_nursery_weight(data_new, 'Сметана'),
                  extract_nursery_weight(data_new, 'Сыр'),
                  extract_nursery_weight(data_new, 'Яйцо'), extract_nursery_weight(data_new, 'Мука пшеничная'),
                  porridge_nursery,
                  extract_nursery_weight(data_new, 'Макаронные изделия "Вермишель"') + extract_nursery_weight(data_new,
                                                                                                              'Макаронные изделия'),
                  extract_nursery_weight(data_new, 'Сахар песок'), confectionary_nursery, dried_fruits_nursery,
                  extract_nursery_weight(data_new, 'Яблоки'),
                  extract_nursery_weight(data_new, 'Сок фруктовый 0,2 для яслей') + extract_nursery_weight(data_new,
                                                                                                           'Сок фруктовый'),
                  extract_nursery_weight(data_new, 'Картофель'), vegetables_nursery,
                  extract_nursery_weight(data_new, 'Хлеб "Ржаной"'),
                  extract_nursery_weight(data_new, 'Хлеб "Пшеничный"') + extract_nursery_weight(data_new,
                                                                                                'Хлеб "Новый"')]

children_weight = [extract_children_weight(data_new, 'Окорок свиной б/к'), extract_children_weight(data_new, 'Мясо ЦБ'),
                   extract_children_weight(data_new, 'Печень говяжья'), extract_children_weight(data_new, 'Минтай'),
                   extract_children_weight(data_new, 'Масло сливочное'),
                   extract_children_weight(data_new, 'Масло растительное'), milk_production_children,
                   extract_children_weight(data_new, 'Творог'), extract_children_weight(data_new, 'Сметана'),
                   extract_children_weight(data_new, 'Сыр'),
                   extract_children_weight(data_new, 'Яйцо'), extract_children_weight(data_new, 'Мука пшеничная'),
                   porridge_children,
                   extract_children_weight(data_new, 'Макаронные изделия "Вермишель"') + extract_children_weight(
                       data_new, 'Макаронные изделия'),
                   extract_children_weight(data_new, 'Сахар песок'), confectionary_children, dried_fruits_children,
                   extract_children_weight(data_new, 'Яблоки'),
                   extract_children_weight(data_new, 'Сок фруктовый 0,2 для яслей') + extract_children_weight(data_new,
                                                                                                              'Сок фруктовый'),
                   extract_children_weight(data_new, 'Картофель'), vegetables_children,
                   extract_children_weight(data_new, 'Хлеб "Ржаной"'),
                   extract_children_weight(data_new, 'Хлеб "Пшеничный"') + extract_children_weight(data_new,
                                                                                                   'Хлеб "Новый"')]

table_total = {'Категории': categories, 'Ясли': nursery_weight, 'Сад': children_weight}

ending_table = pd.DataFrame(table_total)
ending_table.to_excel('Итог.xlsx')


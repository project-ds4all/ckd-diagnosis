from settings import COUNTRY

country_dict = {
    'co': 'Colombia',
    'mx': 'Mexico',
    'br': 'Brasil'
}

default_dict = {
    'co': 336,
    'mx': 308,
    'br': 189
}

cities_experiment = ['Guadalajara', 'Campinas', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba']


def default_cat():
    return default_dict[COUNTRY]


def country_map():
    return country_dict[COUNTRY]

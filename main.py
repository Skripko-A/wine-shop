import collections
import pathlib
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
import datetime
import pandas as pd
import argparse


def parse_wine_xlsx_file():
    parser = argparse.ArgumentParser(description='Запуск сайта элитное вино')
    parser.add_argument('--wine_data', help='Укажите полное имя файла xlsx с данными о винных продуктах')
    return parser.parse_args().wine_data


def make_stock_for_render() -> dict:
    stock_table = pd.read_excel(io=parse_wine_xlsx_file(), na_values='na', keep_default_na=False)
    stock_for_render = collections.defaultdict(list)
    for wine in stock_table.to_dict("records"):
        stock_for_render[wine['Категория']].append(wine)
        wine['Картинка'] = pathlib.Path() / 'images' / wine['Картинка']
    return stock_for_render


def calc_winery_age() -> int:
    current_year = datetime.datetime.today().year
    year_of_foundation = 1920
    winery_age = current_year - year_of_foundation
    return winery_age


def make_winery_age_ending(winery_age) -> str:
    reminder_10 = winery_age % 10
    reminder_100 = winery_age % 100
    winery_age_ending = 'лет'
    if 11 <= reminder_100 <= 19:
        winery_age_ending = 'лет'
    elif 2 <= reminder_10 <= 4:
        winery_age_ending = 'года'
    elif reminder_10 == 1:
        winery_age_ending = 'год'
    return winery_age_ending


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        winery_age_text=f'Уже {calc_winery_age()} {make_winery_age_ending(calc_winery_age())} с вами',
        categorized_wines=make_stock_for_render(),
        categories=make_stock_for_render().keys()
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()

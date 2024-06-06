import collections
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import datetime
import pandas as pd


def get_wines_from_xlsx() -> dict:
    stock_table = pd.read_excel(io='wine3.xlsx', na_values='na', keep_default_na=False)
    columns_titles = stock_table.columns.ravel().tolist()
    columns_values = [stock_table[title].tolist() for title in columns_titles]
    categories, names, sorts, prices, pics, discounts = [value for value in columns_values]
    pics = [f'images/{pic}' for pic in pics]
    stock_params = [[category, name, sort, price, pic, discount]
                    for category, name, sort, price, pic, discount
                    in zip(categories, names, sorts, prices, pics, discounts)]
    stock = []
    for params in stock_params:
        wine = {title: param for title, param in zip(columns_titles, params)}
        stock.append(wine)
    stock_for_render = collections.defaultdict(list)
    for category, wine in zip(categories, stock):
        stock_for_render[category].append(wine)
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


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

rendered_page = template.render(
    winery_age_text=f'Уже {calc_winery_age()} {make_winery_age_ending(calc_winery_age())} с вами',
    categorized_wines=get_wines_from_xlsx(),
    categories=get_wines_from_xlsx().keys()
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()

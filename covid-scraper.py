import click
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime, date
import pdb

@click.command()
@click.option('--date_to_scrape', default=date.today().strftime("%Y%m%d"), help='Date to scrape, today is default.')
def scrape(date_to_scrape):
    date_to_scrape = datetime.strptime(date_to_scrape, "%Y%m%d")

    if date_to_scrape is None:
        print("Incorrect date, please put it in the YYYYmmdd format")
        exit()

    html = make_server_call(date_to_scrape)
    death_data = get_ethnicity_data(html)
    write_csv_from_data(death_data, date_to_scrape)



#Functions
def make_server_call(date_to_scrape):
    date_string = date_to_scrape.strftime("%Y-%m-%d")
    today_string = date.today().strftime("%Y-%m-%d")

    if date_string == today_string:
        url_suffix = 'latest-data'
    else:
        url_suffix = f'latest-data/{date_string}'

    url = f'https://www.chicago.gov/city/en/sites/covid-19/home/{url_suffix}.html'

    response = urlopen(url)
    the_page = response.read()
    return the_page



def get_ethnicity_data(html):
    soup = BeautifulSoup(html, features="html.parser")
    # So it seems that every page is formatted the same, but there's no distinguishing class names or ids
    # my guess is, that it doesn't change at all, and probably won't for awhile. If it's good enough for
    # government work, it's good enough to only do once.
    death_parent_element = soup.find_all("table", limit=2)[1]
    try:
        latinx = list(death_parent_element.select('tr')[15].children)
        black = list(death_parent_element.select('tr')[16].children)
        white = list(death_parent_element.select('tr')[17].children)
        asian = list(death_parent_element.select('tr')[18].children)
        other = list(death_parent_element.select('tr')[19].children)
        unknown = list(death_parent_element.select('tr')[20].children)
    except IndexError:
        print("Error collecting death data, it's probably not available for this date")
        exit()

    latinx_array = [latinx[3].string, latinx[5].string, latinx[7].string]
    black_array = [black[3].string, black[5].string, black[7].string]
    white_array = [white[3].string, white[5].string, white[7].string]
    asian_array = [asian[3].string, asian[5].string, asian[7].string]
    other_array = [other[3].string, other[3].string, other[7].string]
    unknown_array = [unknown[3].string, unknown[5].string, unknown[7].string]

    dictionary = {
        "latinx": latinx_array,
        "black": black_array,
        "white": white_array,
        "asian": asian_array,
        "other": other_array,
        "unknown": unknown_array
    }

    return dictionary



def write_csv_from_data(data, date_to_scrape):
    csv_name = f'covid-deaths-by-ethnicity-{date_to_scrape.strftime("%Y-%m-%d")}.csv'
    with open(csv_name, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow([
            'Characteristic',
            'Deaths',
            '% Deaths Within Group',
            'Rate Per 100k population'
        ])

        for key in data.keys():
            spamwriter.writerow([key] + data[key])

        print(f'🥳 Data written to {csv_name}, you can open it in Excel or Google Docs')



if __name__ == '__main__':
    scrape()

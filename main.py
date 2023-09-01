"""
    Необходимо прописать эту команду: pip install -r requirements.txt
    В файле page.json находятся 2 параметра:
    start_page - ОТКУДА НАЧИНАЕМ (118 стр.)
    end_page - ГДЕ ЗАКАНЧИВАЕМ (119 стр.)
    На момент разработки, доступ к серверу был отключен
    Изменить адрес и токен можно на 95 стр.

"""


import time
import json
from pathlib import Path
import requests
from DrissionPage import ChromiumPage
from DrissionPage.easy_set import set_headless
from bs4 import BeautifulSoup



URL = 'https://vin-history.org/en/catalogue?page='
HOST = 'https://vin-history.org'


def get_hrefs(page_number, page):
    print(f'Starting page {page_number}')
    page.get(URL + str(page_number))
    cloudlare_iframe_detected(page)
    time.sleep(5)
    soup = BeautifulSoup(page.html, 'html.parser')
    all_cars_hrefs = soup.find_all('div', class_='car-title')
    # print(all_cars_hrefs)

    for item in all_cars_hrefs:
        try:
            href = (HOST + item.find('a').get('href'))
            page.get(href)
            soup = BeautifulSoup(page.html, 'html.parser')

            car_details_key = soup.find_all('div', class_='col-md-5 col-7')
            car_details_value = soup.find_all('div', class_='col-md-7 col-5')
            images = soup.find_all('div', class_='col-lg-4 col-md-6 col-sm-12 mb-4')

            if not car_details_key:
                time.sleep(5)
                page.get(href)
                cloudlare_iframe_detected(page)
                time.sleep(5)
                soup = BeautifulSoup(page.html, 'html.parser')
                car_details_key = soup.find_all('div', class_='col-md-5 col-7')

            if not car_details_value:
                time.sleep(5)
                page.get(href)
                cloudlare_iframe_detected(page)
                time.sleep(5)
                soup = BeautifulSoup(page.html, 'html.parser')
                car_details_value = soup.find_all('div', class_='col-md-7 col-5')

            if not images:
                time.sleep(5)
                page.get(href)
                cloudlare_iframe_detected(page)
                time.sleep(5)
                soup = BeautifulSoup(page.html, 'html.parser')
                images = soup.find_all('div', class_='col-lg-4 col-md-6 col-sm-12 mb-4')

            data = {}
            for i, y in enumerate(car_details_key):
                data[car_details_key[i].find(
                    'span'
                ).text.replace("\n", " ").strip()] = car_details_value[i].find(
                    'span'
                ).text.replace("\n", " ").strip()

            if int(data['Year']) > 2016 and float(data['Engine'][0:3]) <= 5:
                res = {
                    "year": soup.find('h1', class_='text-center').text.split(' ')[0][1:],
                    "brand": soup.find('h1', class_='text-center').text.split(' ')[1],
                    "model": str(''.join(soup.find('h1', class_='text-center')).split(' ')[2:-2]).replace(
                        '[', '').replace(',', '').replace(']', '').replace("'", ''),
                    "vin": soup.find('h1', class_='text-center').text.split(' ')[-1][:-1],
                    "odometer": data['Odometer'] if 'Odometer' in data.keys() else "None",
                    "engine": data['Engine'] if 'Engine' in data.keys() else "None",
                    "gearbox": data['Gearbox'] if 'Gearbox' in data.keys() else "None",
                    "drive_train": data['Drive train'] if 'Drive train' in data.keys() else "None",
                    "auction_date": data['Auction date'] if 'Auction date' in data.keys() else "None",
                    "sale_type": data['Sale type'] if 'Sale type' in data.keys() else "None",
                    "damage": data['Damage'] if 'Damage' in data.keys() else "None",
                    "photo": [i.findNext("a").get('href') for i in images],
                    "is_hidden": False,
                    "is_hidden_v2": False
                }
                print(res)
                response = requests.post('http://84.54.47.216/add/cars/', headers={'protection': 'YjWVsPQ6EM!WUaeSsydsPiWHDdp/vbg9JCNefGHltBdddPbb8md0mr=n86hzAyiv'}, json=res)
                print(response.status_code, response.text)
        except Exception:
            print(Exception)
            if 'Just' in soup.find('title').text:
                jsondata = json.loads(Path("page.json").read_text())
                jsondata['startpage'] = page_number
                with open('page.json', 'w') as outfile:
                    json.dump(jsondata, outfile)
            continue

def cloudlare_iframe_detected(page):
    '''
        Проверяем если капча Cloudflare, если есть, то кликаем по кнопке и продолжаем парсинг
    '''
    iframe = page.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
    if iframe:
        iframe('.mark').click()


def main():
    page = ChromiumPage()
    set_headless(False) # Закомментировать, если запускаете не в Docker
    cloudlare_iframe_detected(page)

    json_pages = json.loads(Path("page.json").read_text())

    start_page = json_pages['startpage'] #<= СТАРТУЕМ
    end_page = json_pages['endpage'] #<= ЗАКАНЧИВАЕМ

    for page_number in range(start_page, end_page + 1):
        get_hrefs(page_number, page)
        time.sleep(5)

    page.quit()

if __name__ == "__main__":
    main()

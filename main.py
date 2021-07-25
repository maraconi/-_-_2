import requests
from pprint import pprint
import json
from itertools import zip_longest
import os
import time
from tqdm import tqdm


def get_num():
    while True:
        min_num = 5
        num = input('Укажите количество фото для загрузки(не менее 5):')
        try:
            if int(num) >= min_num:
                break
            else:
                print('Вы указали менее 5 фото.')
        except ValueError:
            print("Некорректный ввод")
    return num


def get_photos_wall():
    num = get_num()
    res = requests.get('https://api.vk.com/method/photos.get', params={'owner_id': params_id,
                                                                       'album_id': album,
                                                                       'access_token': TOKEN,
                                                                       'extended': '1',
                                                                       'count': num,
                                                                       'v': '5.131'}).json()

    c = res['response']['count']
    if c < int(num):
        print('Такого количества фото нет в данном альбоме. Загружаем', c, 'фото.')
    return res


def get_photos_sizes():
    photos_list = data['response']['items']
    max_size_list = []
    for photo in photos_list:
        sizes = photo['sizes']
        max_size = max(sizes, key=get_max_size_photo)
        max_size_list.append(max_size)
    return max_size_list


def get_max_size_photo(size):
    if size['height'] >= size['width']:
        return size['height']
    else:
        return size['width']


def get_photo_name():
    photos_list_all = data['response']['items']
    name_list = []
    for photo in photos_list_all:
        photo_data = photo['date']
        photo_name = photo['likes']['count']
        if photo_name not in name_list:
            name_list.append(photo_name)
        else:
            name_list.append(photo_data)
    return name_list


def download_photo():
    photo_url = get_photos_sizes()
    url_list = []
    for photo in photo_url:
        url = photo['url']
        url_list.append(url)
    filename = get_photo_name()
    if not os.path.exists(album):
        os.mkdir(album)
    for url, name in zip_longest(url_list, filename, fillvalue=''):
        res = requests.get(url).content
        with open(f'{album}/{name}.jpg', 'wb') as f:
            f.write(res)


def get_inform_file():
    photos_sizes = get_photos_sizes()
    photo_types = []
    for photo in photos_sizes:
        photos_type = photo['type']
        photo_types.append({'size': photos_type})
    photo_name = get_photo_name()
    photo_list = []
    for name in photo_name:
        photo_list.append({'file_name': name})
    inform_file = [dict(i, **j) for i, j in zip(photo_types, photo_list)]
    with open(f'{album}/json-файл c фото', 'w') as f:
        json.dump(inform_file, f, indent=2, ensure_ascii=False)
    return inform_file


def put_file_disk():
    url = "https://cloud-api.yandex.net/v1/disk/resources/"
    headers = {"Accept": "application/json",
               "Authorization": token_yd}
    params = {'path': 'Фото с ВК'}
    res = requests.put(url=url, params=params, headers=headers)
    return res.json()


def _get_upload_link(disk_file_path):
    upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {"Accept": "application/json",
               "Authorization": token_yd}
    params = {'path': disk_file_path, 'overwrite': 'true'}
    response = requests.get(upload_url, headers=headers, params=params)
    return response.json()


def upload_file_disk():
    inform_list = get_inform_file()
    path = os.path.join(os.getcwd(), album)
    for address, dirs, photos in os.walk(path):
        for photo in photos:
            href = _get_upload_link(disk_file_path=f'Фото с ВК/{photo}').get('href', '')
            response = requests.put(href, data=open(f'{address}\{photo}', 'rb'))
            for i in tqdm(photo):
                time.sleep(1)
            response.raise_for_status()
            if response.status_code == 201:
                print('Файл успешно загружен')
    print('Загруженные файлы на YandexDisk:')
    pprint(inform_list)


if __name__ == '__main__':
    TOKEN = 'ХХХ'
    params_id = input('Введите id пользователя:')
    token_yd = input('Введите token Яндекс.Диска:')
    album = input('Введите наименование альбома (wall, profile, saved):')
    data = get_photos_wall()
    download_photo()
    put_file_disk()
    upload_file_disk()

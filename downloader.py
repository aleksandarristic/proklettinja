import json
import os
import subprocess

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import urllib3
urllib3.disable_warnings()


def create_name(url):
    return urlparse(url).path.strip('/').split('/')[-1].replace(' ', '-') + '.mp3'


def get_urls(page):
    urls = []
    req = requests.get(page, verify=False)
    soup = BeautifulSoup(req.text, 'html.parser')
    print('Working on iframes', end='')
    for iframe in soup.find_all('iframe'):
        base_url = iframe.get('src')
        print('.', end='', flush=True)
        r = requests.get(base_url, verify=False)
        iframe_soup = BeautifulSoup(r.text, 'html.parser')
        for element in iframe_soup.find_all('source'):
            url = urljoin(base_url, element.get('src'))
            name = create_name(base_url)
            urls.append((url, name))
    print(f'Total of {len(urls)} urls found to download on page "{page}".')
    return urls


def download(book_dir_path, url_list):
    cmd = ['aria2c', '-i', f'{url_list}', '-d', f'{book_dir_path}']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    proc.wait()
    output, errors = proc.communicate()
    print(output)
    if errors:
        print(errors)


def main():
    # load config
    with open(os.path.realpath(os.path.join('config', 'config.json')), 'r') as f:
        config = json.loads(f.read())

    # iterate through subjects
    for subject, subject_data in config.get('subjects', {}).items():
        print(f'Working on subject "{subject}"...')

        # iterate through books
        for book, page_url in subject_data.items():
            print(f'Working on "{book}"...')

            book_urls = get_urls(page_url)
            book_dir_path = os.path.realpath(os.path.join(config.get('output', ''), subject, book))
            url_list_path = os.path.realpath(os.path.join(book_dir_path, 'url_list.txt'))

            try:
                os.makedirs(book_dir_path)
                print(f'Directory "{book_dir_path}" created.')
            except FileExistsError:
                print(f'Directory "{book_dir_path}" already exists.')
            except Exception as e:
                print(f'Error creating "{book_dir_path}": {e}')

            # create an url list for this book
            with open(url_list_path, 'w') as f:
                for url, name in book_urls:
                    f.write(f'{url}\n\tout={name}\n')

            print(f'File list saved to "{url_list_path}".')
            print(f'Downloading with aria2c...')

            # feed the url list and the book directory to aria2c for download
            download(book_dir_path, url_list_path)
            print(f'Done working on "{book}".')

        print(f'Done working on subject "{subject}".')
    print('All done!')


if __name__ == '__main__':
    main()

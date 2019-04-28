#!/usr/bin/python3

import logging
import os
import socket
import shutil
import traceback
from random import randint
from time import sleep

import click
import requests
import simplejson as json

from fake_useragent import UserAgent
from googletrans import Translator

OUTPUT_DIR = 'output'
IMAGE_DIR = 'images'
ORIGIN_JSON_URL = 'https://roostaq.github.io/irasutoya-data/irasutoya.json'
OUTPUT_JSON_FILE_NAME = 'irasutoya_with_en.json'

TRANSLATE_SERVICE_URLS = ['translate.google.com', 'translate.google.co.jp']


def _init():
    """Initialize
    """
    logging.basicConfig(
        format='%(asctime)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=logging.INFO)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _get_irasutoya_json(start_at=0):
    """Get the original irasutoya's json

    If the json file doesn't exists, download it to local file. Once the json
    file is located in local file system, deserialize it to Python object.

    Args:
        start_at: The position to start, default is start from beginning

    Returns:
        A dict object contains data from irasutoya's json
    """
    filename = os.path.join(OUTPUT_DIR,
                            _get_filename_from_url(ORIGIN_JSON_URL))
    if not os.path.exists(filename):
        _download_file(ORIGIN_JSON_URL, OUTPUT_DIR)

    with open(filename, encoding='utf-8') as f:
        return json.load(f)[start_at:]


def _translate(text: str, dest='en') -> str:
    """Translate a text to destination language

    If the given text is None or Falsy, an empty string is returned

    Args:
        text: Text to be translated
        dest: The destination language to translate to, default is English

    Returns:
        Translated text in destination language
    """
    if not text or text is None:
        return ''
    logging.info('Translating {}'.format(text))
    translation = Translator(
        service_urls=TRANSLATE_SERVICE_URLS,
        user_agent=UserAgent().random).translate(
            text, dest=dest)

    sleep(randint(3, 6))

    return [x.text for x in translation] if isinstance(
        translation, list) else translation.text


def _download_file(url: str, dest: str = '.'):
    """Download file from a given url

    Download file and save it to local. The filename is auto determined by the
    url.

    Args:
        url: The file's url need to be downloaded
        dest: The destination directory to save the downloaded file

    Returns:
        The local file name
    """
    os.makedirs(dest, exist_ok=True)
    local_filename = _get_filename_from_url(url)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(dest, local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

    return local_filename


def _transform(original: dict) -> dict:
    """Transform an object from irasutoya's json to new desired object

    Args:
        original: The dict as a single data from irasutoya's json

    Returns:
        The object with new added key-value pairs
    """
    filename = _get_filename_from_url(original.get('image_url', ''))

    new_obj = {**original}
    new_obj['title_en'] = _translate(new_obj.get('title', ''))
    new_obj['description_en'] = _translate(new_obj.get('description', ''))
    new_obj['categories_en'] = _translate(new_obj.get('categories', ''))
    new_obj['image_alt_en'] = _translate(new_obj.get('image_alt', ''))

    year, month = _get_publibed_year_month(original.get('published_at', ''))
    new_obj['directory_path'] = os.path.join('.', IMAGE_DIR, year, month,
                                             filename)

    return new_obj


def _get_filename_from_url(url: str) -> str:
    """Get the filename from url

    Args:
        url: The url

    Returns:
        The filename
    """
    return url.split('/')[-1]


def _get_publibed_year_month(published_at: str) -> (str, str):
    """Get the publish's year and month from the publish time

    Args:
        published_at: The published time

    Return:
        A corresponding (year, month) as a tuple
    """
    year, month = published_at.split(' ')[0].split('-')[:-1]
    return (year, month)


def _process(illustrations: list, download: bool, translate: bool, max_retries: int) -> list:
    """Process the irasutoya's json

    Args:
        illustrations: The original irasutoya's json illustrationa as a list
        of illustration data
        download: whether or not download the images
        translate: whether or not translate to English

    Returns:
        The new list of dicts which contain the original data with new added
        fields
    """

    for illustration in illustrations:

        job_done = False

        for attempt in range(max_retries):

            try:

                new_obj = _transform(illustration) if translate else illustration

                year, month = _get_publibed_year_month(
                    new_obj.get('published_at', ''))
                if download:
                    logging.info('Downloading image from {}'.format(
                        new_obj.get('image_url')))
                    _download_file(
                        new_obj.get('image_url'),
                        os.path.join(OUTPUT_DIR, IMAGE_DIR, year, month))

                job_done = True

            except (socket.gaierror, socket.error, socket.timeout) as e:
                logging.info('Network error! Retrying after 30 seconds...')
                logging.info(e)
                if attempt >= (max_retries-1):
                    logging.error('Max retries reached, exiting.')
                    return
                else:
                    sleep(30)
            except (KeyboardInterrupt, SystemExit) as e:
                logging.info('User abort!')
                logging.info(e)
                return
            except:
                traceback.print_exc()
                logging.error('Exception not implemented!')
                logging.error(e)
                return

            if job_done:
                break

        yield new_obj


@click.command()
@click.option('-d', '--download', is_flag=True, help='Download images')
@click.option(
    '-t',
    '--translate',
    is_flag=True,
    help='Create and translate original json to english')
@click.option('-r', '--retries', default=10, help='Max retries if problem occurs (network or API)')

def main(download, translate, retries):
    """
    Main function
    """
    _init()

    # when both 'download' and 'translate' parameters are not passed, trat them
    # as True by default
    argument_not_passed = not download and not translate
    download = download or argument_not_passed
    translate = translate or argument_not_passed

    output_file = os.path.join(OUTPUT_DIR, OUTPUT_JSON_FILE_NAME)
    output_json = []
    if os.path.exists(output_file):
        with open(output_file, encoding='utf-8') as f:
            output_json = json.load(f)

    for result in _process(
            _get_irasutoya_json(len(output_json)), download, translate, retries):
        output_json.append(result)

    if translate:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                output_json,
                f,
                ensure_ascii=False,
                iterable_as_array=True,
                indent=4)


if __name__ == "__main__":
    main()

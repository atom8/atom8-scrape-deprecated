import datetime
import json
import os
import sys
import urllib
import time


# ./../settings.json
DEFAULT_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../settings.json')


def create_directory(directory_path):
    """Creates a directory."""
    try:
        os.makedirs(directory_path, exist_ok=False)
    except OSError:
        if (os.listdir(directory_path)):
            print('[ERROR] Folder already exists: %s.' % (directory_path))
            raise OSError('Folder already exists')


def download_image_from_url(url, directory, filename=None):
    """Download an image from a URL.

    Args:
        url (str): The url of the image to download.

        directory (str): The directory to download the image to.

        filename (str, optional): The filename to save the image under. If no
            filename is specified then saved under url.
    """

    if filename is None:
        filename = url.split('/')[-1]

    # check if filename exists, if so: append a unique number to it
    base_filename = filename
    x = 0
    while filename in os.listdir(directory):
        x += 1
        filename = base_filename + str(x)

    try:
        urllib.request.urlretrieve(url, os.path.join(directory, filename))
    except (OSError, urllib.error.HTTPError):
        print('[ERROR] Could not download: ' + url)


def export_settings(export_destination, settings_dict):
    with open(export_destination, 'w') as f:
        json.dump(settings_dict, f, indent=4)


def find_desktop():
    # Find desktop path

    if sys.platform.startswith('win'):
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    elif sys.platform.startswith('linux'):
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    else:
        # TODO apple
        print("Cannot find desktop, returning working directory")
        return os.getcwd()


def retrieve_JSON(filename):
    """Retrieve settings for scraper.

    Note:
        After loading settings this function saves settings to a global, so
        that settings only needs to be saved once.

    Args:
        settings_filename (str): the path to the settings file.

    Returns:
        dict: the scraper settings.
    """

    with open(filename) as json_file:
        json_data = json.load(json_file)
    return json_data


def refresh_scraper_settings(settings_filename):
    global SETTINGS
    with open(settings_filename) as settings_file:
        SETTINGS = json.load(settings_file)


def timestamp_directory(directory_path, prefix='export'):
    """Returns a timestamped directory path."""
    t = time.time()
    timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')
    return os.path.join(directory_path, prefix + timestamp)


def verbose_iter(lst, message):
    tot_length = len(lst)
    curr = 0

    for item in lst:
        curr += 1
        print("%s (%d/%d)" % (message, curr, tot_length))
        yield item

import json
import os
import sys
import urllib


SETTINGS = None


def create_directory(directory_path):
    """Creates a directory."""
    try:
        os.makedirs(directory_path, exist_ok=False)
    except OSError:
        if (os.listdir(directory_path)):
            print('[ERROR] Folder already exists: %s.' % (directory_path))


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


def get_scraper_settings(settings_filename):
    """Retrieve settings for scraper.

    Note:
        After loading settings this function saves settings to a global, so
        that settings only needs to be saved once.

    Args:
        settings_filename (str): the path to the settings file.

    Returns:
        dict: the scraper settings.
    """

    global SETTINGS

    if SETTINGS is None:
        with open(settings_filename) as settings_file:
            SETTINGS = json.load(settings_file)
            
    return SETTINGS
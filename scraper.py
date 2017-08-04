import click
import datetime
import json
import os
import sys
import reddit as reddit_control
import time
import urllib

DESKTOP_IDENTIFIER = 'desktop*'
SETTINGS = None


def download_image_from_url(url, directory, filename=None):
    if filename is None:
        filename = url.split('/')[-1]

    # check if filename exists, if so: append a unique number to it
    base_filename = filename
    x = 0
    while filename in os.listdir(directory):
        x += 1
        filename = base_filename + x

    urllib.request.urlretrieve(url, os.path.join(directory, filename))


def get_scraper_settings(settings_filename):
    global SETTINGS

    if SETTINGS is None:
        with open(settings_filename) as settings_file:
            SETTINGS = json.load(settings_file)
    return SETTINGS


def create_folder(export_folder):
    try:
        os.makedirs(export_folder, exist_ok=False)
    except OSError:
        if (os.listdir(export_folder)):
            print('[ERROR] Export folder already exists')


def get_export_folder(prefix='export'):
    export_directory = click.prompt('Export directory', type=str, default=DESKTOP_IDENTIFIER)

    # Find desktop path
    if export_directory == DESKTOP_IDENTIFIER:
        if sys.platform.startswith('win'):
            export_directory = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif sys.platform.startswith('linux'):
            export_directory = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            # TODO apple
            print("Cannot find desktop, using working directory")
            export_directory = os.cwd()

    # Create export folder, with timestamp
    t = time.time()
    timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')
    return os.path.join(export_directory, prefix + timestamp)


def scrape_reddit(settings, export_folder, verbose=False):
    subreddits = settings['subreddits']

    # Retrieve reddit posts
    # TODO different date ranges
    reddit_posts = []
    for subreddit in subreddits:
        subreddit_posts = reddit_control.get_posts_by_date(
            subreddit=subreddit['name'],
            min_score=subreddit['min_karma'],
            days=7,
            verbose=True
        )
        reddit_posts += subreddit_posts

    # Export post data
    # TODO sort posts by highest karma
    with open(os.path.join(export_folder, 'export_reddit.json'), 'w') as f:
        json.dump(reddit_posts, f, indent=4)

    # Extract post data and export images
    # TODO download gifv and webm
    for post in reddit_posts:
        try:
            image_url = post['url']
            if verbose:
                print(image_url)
            
            domain = post['domain']
            if domain == 'gfycat.com':
                image_url = image_url[:8] + 'zippy.' + image_url[8:] + '.webm'
            if image_url.endswith('gifv'):
                image_url = image_url[:-4] + 'mp4'

            download_image_from_url(image_url, export_folder)

        except (FileNotFoundError, OSError) as e:
            print("Ignored")
            pass


@click.group()
def scraper():
    pass


@scraper.command()
def all():
    export_folder = get_export_folder()
    create_folder(export_folder)
    # create_folder(export_folder, reddit)

    settings = get_scraper_settings('settings.json')

    # perform scrapes
    scrape_reddit(settings, export_folder)


@scraper.command()
def reddit():
    export_folder = get_export_folder(prefix='reddit')
    create_folder(export_folder)
    settings = get_scraper_settings('settings.json')

    scrape_reddit(settings, export_folder)


if __name__ == "__main__":
    scraper()

import click
import datetime
import json
import os
import sys
import time

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
    if SETTINGS is None:
        with open(settings_filename) as settings_file:
            SETTINGS = json.load(settings_file)
    return SETTINGS


@click.group()
def scraper():
    pass

@scraper.command()
@click.option('--export_directory', prompt='Output directory', type=str, default=DESKTOP_IDENTIFIER)
def all(export_directory):
    # Find desktop path
    if export_directory == DESKTOP_IDENTIFIER:
        if sys.platform.startswith('win'):
            export_directory = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif sys.platform.startswith('linux'):
            export_directory = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            return  # TODO properly exit

    # Create export folder, with timestamp
    t = time.time()
    timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')
    export_folder = os.path.join(export_directory, 'export' + timestamp)
    try:
        os.makedirs(export_folder, exist_ok=False)
    except OSError:
        if (os.listdir(export_folder)):
            print('[ERROR] Export folder already exists')
            return
    print('Exporting to ' + export_folder)

    # perform scrapes
    reddit()


@scraper.command()
def reddit():
    settings = get_scraper_settings()
    subreddits = settings['subreddits']

    # Retrieve reddit posts
    # TODO different date ranges
    reddit_posts = []
    for subreddit in SUBREDDITS:
        subreddit_posts = reddit_cron.get_posts_by_date(
            subreddit=subreddit['name'],
            min_score=subreddit['min_karma'],
            days=7,
            verbose=True
        )
        reddit_posts += subreddit_posts

    # Export post data
    # TODO sort posts by highest karma
    with open(os.path.join(export_directory, 'export_reddit.json'), 'w') as f:
        json.dump(reddit_posts, f, indent=4)

    # Extract post data and export images
    # TODO download gifv and webm
    for post in reddit_posts:
        try:
            image_url = post['url']
            print(image_url)  # TODO if verbose
            download_image_from_url(image_url, export_directory)
        except (FileNotFoundError, OSError) as e:
            print("Ignored")
            pass


if __name__ == "__main__":
    scraper()

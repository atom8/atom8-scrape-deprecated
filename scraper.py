#!/usr/bin/python3

import click
import time
import datetime
import reddit
import json
import os
import urllib.request


# TODO get median karma
# pull every post in top 25% of karma
# Research subs:

# author
# date
# content
# title


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


def main():
    # TODO allow for specifying output directory
    t = time.time()
    timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')
    export_directory = os.path.join(os.getcwd(), 'export' + timestamp)
    try:
        os.makedirs(export_directory, exist_ok=False)
    except OSError:
        if (os.listdir(export_directory)):
            print('[ERROR] Export directory already exists')
            return
    print('Exporting to ' + export_directory)

    # Retrieve settings
    settings = None
    with open('settings.json') as settings_file:
        settings = json.load(settings_file)
    SUBREDDITS = settings['subreddits']

    # Retrieve reddit posts
    # TODO different date ranges
    reddit_posts = []
    for subreddit in SUBREDDITS:
        subreddit_posts = reddit.get_posts_by_date(
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


if __name__ == '__main__':
    main()

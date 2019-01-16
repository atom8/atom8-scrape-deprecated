"""GDI Scraper utility

The GDI Scraper utility scrapes images from the web to be processed for the GDI
queue.

"""

import click
import datetime
import json
import os
import sys
import time

from . import etc
from . import reddit as reddit_control
from . import tigsource as tig_control


def determine_export_folder(prefix='export'):
    # prompt user for export directory
    export_directory = click.prompt(
        'Export directory (defaults to desktop)', type=str, default=None)


    # use desktop by default
    if export_directory == None:
        export_directory = etc.find_desktop()

    # get current time
    t = time.time()
    timestamp = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')

    # folder name = prefix + the current time
    export_folder_name = os.path.join(export_directory, 'export' + timestamp)

    # create export folder using etc function
    etc.create_folder(export_folder)




@click.group()
def scraper():
    pass


@scraper.command()
def all():
    export_folder = determine_export_folder()
    etc.create_folder(export_folder)
    # create_folder(export_folder, reddit)

    settings = etc.get_scraper_settings('settings.json')

    # perform scrapes
    click.secho("\nPerforming Reddit scrape", fg='yellow')
    reddit.scrape(subreddits['reddit']['subreddits'], export_folder)

    click.secho("\nPerforming TIGSource scrape", fg='yellow')
    tigsource.scrape(settings, export_folder)

    click.secho("\nTASK COMPLETE!", fg='green')


@scraper.command()
def reddit():
    export_folder = determine_export_folder(prefix='reddit')
    etc.create_folder(export_folder)

    settings = etc.get_scraper_settings('settings.json')

    reddit.scrape(settings['reddit']['subreddits'], export_folder)


@scraper.command()
def tigsource():
    export_folder = determine_export_folder(prefix='tigsource')
    etc.create_folder(export_folder)

    settings = etc.get_scraper_settings('settings.json')

    tigsource.scrape(settings['tigsource'], export_folder)

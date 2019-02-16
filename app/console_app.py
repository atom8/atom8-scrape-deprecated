"""GDI Scraper utility

The GDI Scraper utility scrapes images from the web to be processed for the GDI
queue.

"""

import click

from . import etc
from . import instagram as insta_control
from . import reddit as reddit_control
from . import tigsource as TIG_control
from . import tumblr as tumblr_control
from . import twitter as twitter_control


def determine_export_destination(prefix='export'):
    # prompt user for export directory
    requested_export_directory_path = click.prompt(
        'Specify directory to export to (defaults to desktop)',
        type=str, default='')

    # use desktop by default
    if requested_export_directory_path == '':
        export_directory_path = etc.find_desktop()
    else:
        export_directory_path = requested_export_directory_path

    return etc.timestamp_directory(export_directory_path, prefix=prefix)


@click.group()
def scraper():
    pass


@scraper.command()
def all():
    export_directory = determine_export_destination()
    etc.create_directory(export_directory)

    days = click.prompt('How many days to scrape', type=int, default=7)

    settings = etc.retrieve_JSON('settings.json')

    # perform scrapes
    click.secho('\nPerforming Instagram scrape', fg='yellow')
    insta_control.scrape(
        settings['instagram']['profiles'], export_directory, days=days)

    click.secho("\nPerforming Reddit scrape", fg='yellow')
    reddit_control.scrape(
        settings['reddit']['subreddits'], export_directory, days=days)

    click.secho("\nPerforming TIGSource scrape", fg='yellow')
    TIG_control.scrape(
        settings['tigsource']['topics'], export_directory, days=days)

    click.secho("\nPerforming Tumblr scrape", fg='yellow')
    tumblr_control.scrape(
        settings['tumblr']['blogs'], export_directory, days=days)

    click.secho("\nPerforming Twitter scrape", fg='yellow')
    twitter_control.scrape(
        settings['twitter']['users'], export_directory, days=days)

    click.secho("\nTASK COMPLETE!", fg='green')


@scraper.command()
def instagram():
    export_directory = determine_export_destination(prefix='instagram')
    etc.create_directory(export_directory)

    settings = etc.retrieve_JSON('settings.json')

    insta_control.scrape(
        settings['instagram']['profiles'], export_directory)


@scraper.command()
def reddit():
    export_directory = determine_export_destination(prefix='reddit')
    etc.create_directory(export_directory)

    settings = etc.retrieve_JSON('settings.json')

    reddit_control.scrape(
        settings['reddit']['subreddits'], export_directory)


@scraper.command()
def tigsource():
    export_directory = determine_export_destination(prefix='tigsource')
    etc.create_directory(export_directory)

    settings = etc.retrieve_JSON('settings.json')

    TIG_control.scrape(
        settings['tigsource']['topics'], export_directory)


@scraper.command()
def tumblr():
    export_directory = determine_export_destination(prefix='tigsource')
    etc.create_directory(export_directory)

    settings = etc.retrieve_JSON('settings.json')

    tumblr_control.scrape(
        settings['tumblr']['blogs'], export_directory)


@scraper.command()
def twitter():
    export_directory = determine_export_destination(prefix='twitter')
    etc.create_directory(export_directory)

    settings = etc.retrieve_JSON('settings.json')

    twitter_control.scrape(
        settings['twitter']['users'], export_directory)

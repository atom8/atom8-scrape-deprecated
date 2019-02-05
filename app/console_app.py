"""GDI Scraper utility

The GDI Scraper utility scrapes images from the web to be processed for the GDI
queue.

"""

import click

from . import etc
from . import reddit as reddit_control
from . import tigsource as TIG_control
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
    # create_directory(export_directory, reddit)

    settings = etc.get_scraper_settings('settings.json')

    # perform scrapes
    click.secho("\nPerforming Reddit scrape", fg='yellow')
    reddit_control.scrape(settings['reddit']['subreddits'], export_directory,
                          verbose=True)

    click.secho("\nPerforming TIGSource scrape", fg='yellow')
    TIG_control.scrape(settings['tigsource']['topics'], export_directory,
                       verbose=True)

    click.secho("\nTASK COMPLETE!", fg='green')


@scraper.command()
def reddit():
    export_directory = determine_export_destination(prefix='reddit')
    etc.create_directory(export_directory)

    settings = etc.get_scraper_settings('settings.json')

    reddit_control.scrape(settings['reddit']['subreddits'], export_directory,
                          verbose=True)


@scraper.command()
def tigsource():
    export_directory = determine_export_destination(prefix='tigsource')
    etc.create_directory(export_directory)

    settings = etc.get_scraper_settings('settings.json')

    TIG_control.scrape(settings['tigsource'], export_directory,
                       verbose=True)


@scraper.command()
def twitter():
    export_directory = determine_export_destination(prefix='twitter')
    etc.create_directory(export_directory)

    settings = etc.get_scraper_settings('settings.json')

    twitter_control.scrape(settings['twitter']['users'], export_directory,
                           verbose=True)

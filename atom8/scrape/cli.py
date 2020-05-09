"""Atom8 Scrape - Command Line Interface

A CLI tool used to operate Atom8 Scrape integrations. These integrations scrape
images from the web to be processed by Atom8 Curate.
"""

import click

from . import etc, integrations


def load_settings(ctx, path):
    """Load settings from a provided path. Will abort if settings is not found.

    Args:
        ctx (click.Context)

        path (str): path to settings
    """
    try:
        settings_file = etc.retrieve_JSON(path)
    except FileNotFoundError:
        ctx.fail("File not found")

    return settings_file


def vecho(ctx, message, **kwargs):
    """Print, using echo, if verbose is true"""
    if ctx.obj.get('verbose'):
        click.secho(message, **kwargs)


@click.group()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.pass_context
def main(ctx, verbose):
    """atom8 - scrape

    Scrape from popular social media websites using various conditions and
    export to target directory.
    """

    # Verify context exists
    ctx.ensure_object(dict)

    # Verbosity
    ctx.obj['verbose'] = verbose


@main.command()
@click.option('-s', '--settings', default=None, help='use a settings file')
@click.pass_context
def gui(ctx, settings):
    """Launch the GUI editor"""
    from atom8scrape import gui

    if settings is not None:
        vecho(ctx, "Loading settings: %s" % settings)
        # TODO gui.run_app(settings=load_settings(ctx, settings))
    gui.run_app()


@main.command()
@click.option('-e', '--exportdir', default='desktop',
              help='specify export directory (desktop)')
@click.option('-d', '--depth', default=3,
              help='number of days to scrape (3)')
@click.argument('settings_path', nargs=1, type=click.Path(exists=True),
                required=True)
@click.argument('target', nargs=-1, required=True)
@click.pass_context
def scrape(ctx, exportdir, depth, settings_path, target):
    """Perform scrape.

    Requires a settings file.
    """

    # Load settings
    vecho(ctx, "Loading settings: %s" % settings_path, fg='magenta')
    settings = load_settings(ctx, settings_path)

    # Determine export directory
    if exportdir == 'desktop' or exportdir == '':
        exportdir = etc.find_desktop()
    export_directory = etc.prepend_timestamp_directory(exportdir)
    ctx.obj['export_directory'] = export_directory

    # Save the duration to context
    ctx.obj['depth'] = depth

    # Create export directory (print, if verbose)
    vecho(ctx, "Creating export directory at: %s" % export_directory,
          fg='magenta')
    etc.create_directory(export_directory)

    #
    # BEGIN SCRAPING
    #

    vecho(ctx, "START SCRAPE", fg='yellow')

    scrape_all = 'all' in target
    if scrape_all:
        vecho(ctx, "Scraping all integrations", fg='yellow')

    if 'instagram' in target or scrape_all:
        vecho(ctx, '\nPerforming Instagram scrape', fg='yellow')
        integrations.instagram.scrape(
            settings['instagram']['profiles'], export_directory, days=depth)

    if 'reddit' in target or scrape_all:
        vecho(ctx, "\nPerforming Reddit scrape", fg='yellow')
        integrations.reddit.scrape(
            settings['reddit']['subreddits'], export_directory, days=depth)

    if 'tigsource' in target or scrape_all:
        vecho(ctx, "\nPerforming TIGSource scrape", fg='yellow')
        integrations.tigsource.scrape(
            settings['tigsource']['topics'], export_directory, days=depth)

    if 'tumblr' in target or scrape_all:
        vecho(ctx, "\nPerforming Tumblr scrape", fg='yellow')
        integrations.tumblr.scrape(
            settings['tumblr']['blogs'], export_directory, days=depth)

    if 'twitter' in target or scrape_all:
        vecho(ctx, "\nPerforming Twitter scrape", fg='yellow')
        integrations.twitter.scrape(
            settings['twitter']['users'], export_directory, days=depth)

    vecho(ctx, "\nEND SCRAPE", fg='yellow')

import instaloader
from datetime import datetime, timedelta
from .. import etc


def scrape(profiles, export_directory, days=7, verbose=True):

    L = instaloader.Instaloader()

    expire_date = datetime.now() - timedelta(days=days)

    if verbose:
        profiles = etc.verbose_iter(profiles, 'Scanning insta profiles')

    pending_posts = []
    for profile in profiles:
        p = None
        try:
            p = instaloader.Profile.from_username(L.context, profile)
        except instaloader.exceptions.ProfileNotExistsException:
            print("[WARN] Profile does not exist: '%s'." % profile)
            continue

        posts = p.get_posts()
        for post in posts:
            if verbose:
                print('.', end='')

            if post.date > expire_date:
                pending_posts.append(post)
            else:
                break

        if verbose:
            print('')

    if verbose:
        pending_posts = etc.verbose_iter(
            pending_posts, 'Downloading insta photos')

    for post in pending_posts:
        post_name = post.shortcode + '.jpg'

        metadata = {
            'author': post.owner_username,
            'date': str(post.date),
            'ref': post_name,
            'source': 'http://instagram.com/p/' + post.shortcode,
            'text': post.caption
        }

        etc.download_image_from_url(
            post.url, export_directory, post_name,
            metadata=metadata)

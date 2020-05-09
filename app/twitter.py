import twitter_scraper
from datetime import datetime, timedelta
from . import etc


def scrape(users, export_directory, days=7, verbose=True):

    expire_date = datetime.now() - timedelta(days=days)

    if verbose:
        users = etc.verbose_iter(users, 'Scanning twitter feeds')

    photos = []
    for user in users:

        # Don't exit on the first tweet because it could be a pinned tweet and
        # that messes up the time comparisons
        first_tweet = True

        for tweet in twitter_scraper.get_tweets(user):
            if verbose:
                print('.', end='')  # An indicator for each tweet read

            tweet_time = tweet.get('time')
            if tweet_time > expire_date:
                tweet_photos = tweet.get('entries').get('photos')

                if tweet_photos:
                    for photo_url in tweet_photos:
                        photo_name = photo_url.split('/')[-1]

                        meta = {
                            'author': user,
                            'date': str(tweet_time),
                            'ref': photo_name,
                            'source': photo_url,
                            'text': tweet['text']
                        }

                        photos.append(meta)

            elif not first_tweet:
                break
            first_tweet = False

        if verbose:
            print('')  # newline

    if verbose:
        photos = etc.verbose_iter(photos, 'Downloading twitter images')

    for photo_meta in photos:
        etc.download_image_from_url(photo_meta['source'], export_directory,
                                    photo_meta['ref'], metadata=photo_meta)

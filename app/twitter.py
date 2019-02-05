import twitter_scraper
import etc


def scrape():
    for tweet in twitter_scraper.get_tweets('_shellbot_', pages=1):
        photos = tweet.get('entries').get('photos')
        for photo in photos:
            print(photo)
            etc.download_image_from_url(
                photo,
                etc.find_desktop(),
                photo.split('/')[-1])


if __name__ == '__main__':
    scrape()

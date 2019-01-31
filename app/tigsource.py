import re
import lxml.html
import requests
from datetime import datetime, timedelta
from . import etc


MAX_POST_CAP = 2**16
POST_STEP = 20
DATE_REGEXP = re.compile(r'[A-Za-z]{3,9} [0-9]{1,2}, [0-9]{4}')


def download_images(d, export_folder):
    for image_url in d:
        etc.download_image_from_url(image_url, export_folder)


def get_posts_by_date(topic_num, days=7, verbose=False):
    '''
    Retrieve posts from a thread
    '''

    # BASE_REQUEST + POST_CAP - 20x
    # Where x is the amount of pages to traverse backwards
    BASE_REQUEST = 'https://forums.tigsource.com/index.php?topic={}.'\
                   .format(topic_num)

    # Use any timezone as long as we use the same when converting post UTC
    expire_date = datetime.now() - timedelta(days=days)

    # Initial scan
    response = requests.get(BASE_REQUEST + str(MAX_POST_CAP))
    tree = lxml.html.fromstring(response.content)

    subject = tree.xpath('//td[@id="top_subject"]/text()')
    if verbose:
        print(subject)

    # Calculate the max post num
    reply_nums = tree.xpath('//div[@class="smalltext"]/b/text()')
    post_num = MAX_POST_CAP
    for reply_num in reply_nums:
        if re.search(r'Reply #[0-9]+ on:', reply_num):
            current_post_num = int(re.findall(r'\d+', reply_num)[0])
            post_num = min(post_num, current_post_num)

    processing = True
    images = []
    while processing:
        response = requests.get(BASE_REQUEST + str(post_num))
        tree = lxml.html.fromstring(response.content)

        # Parse unicode date from post header and check if processing
        dates = tree.xpath('//div[@class="smalltext"]/text()')
        for raw_date in dates:
            date_match = DATE_REGEXP.search(raw_date)
            if date_match:
                date = datetime.strptime(date_match.group(0), "%B %d, %Y")

                if date < expire_date:
                    processing = False

        images += tree.xpath('//div[@class="post"]/img/@src')
        post_num -= POST_STEP

    return images


def get_topic_images(t, verbose=False, days=7):
    out = []
    for topic in t:
        out += get_posts_by_date(topic, verbose,  days)
    return out


def scrape(topics, export_directory, verbose=False, days=7):
    """Perform tigsource scrape routine."""

    images = []
    if verbose:
        images = get_topic_images(
            etc.verbose_iter(topics, 'Scanning TIGforum topics'),
            verbose=verbose, days=days)
        download_images(
            etc.verbose_iter(images, 'Download TIGforum images'),
            export_directory)
    else:
        images = get_topic_images(topics)
        download_images(images, export_directory)

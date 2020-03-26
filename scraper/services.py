from datetime import datetime
import requests
from selenium import webdriver
from django.conf import settings
from time import sleep
import json
from insta_manager.models import UserInstagram, Follower, Post


def initialize_scraper():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--lang=en_US')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
    driver = webdriver.Chrome(executable_path=settings.CHROME_PATH, options=options)
    return driver


def login_get_cookies(user_ig: UserInstagram) -> dict:
    driver = initialize_scraper()
    driver.get("http://instagram.com/accounts/login")
    sleep(3)
    user = driver.find_element_by_xpath("//*[@name='username']")
    user.send_keys(user_ig.username)
    pw = driver.find_element_by_xpath("//*[@name='password']")
    pw.send_keys(user_ig.password)
    sleep(2)
    # driver.find_element_by_xpath("//*[@type='submit']").click()
    driver.find_element_by_tag_name('form').submit()
    sleep(10)
    cookies = driver.get_cookies()
    user_ig.lastActive = datetime.now()
    user_ig.save()
    return cookies

def fetch_data(follower: Follower):
    fetch_stories_url = get_story_url(follower.user_id)
    fetch_posts_url = get_posts_url(follower.username)
    session = requests.session()
    session.headers.update(get_active_headers())

    cookies = get_active_cookies(follower.owner)
    for cookie in cookies:
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    res = session.get(fetch_stories_url)
    stories = res.json()['data']['reels_media']
    fetch_stories(follower, stories)
    res = session.get(fetch_posts_url)
    posts = res.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
    fetch_posts(follower, posts)


def fetch_stories(follower: Follower, stories: dict):
    # Check whether there are new stories
    if len(stories) == 0:
        return
    # Iterate through all stories
    try:
        for i in range(len(stories)):

            uploaded_at = datetime.fromtimestamp(int(stories[i]['taken_at_timestamp']))
            if uploaded_at <= follower.lastStory:
                continue

            if stories[i]['is_video']:
                fetch_url = stories[i]['video_resources'][0]['src']
                extension = "_story.mp4"
            else:
                fetch_url = stories[i]['display_url']
                extension = "_story.jpg"
            new_post = Post(owner=follower, uploadedAt=uploaded_at, type=Post.PostType.STORY, url=fetch_url)
            follower.lastStory = uploaded_at
            folder_name = "/stories/" + follower.username + "/"
            new_post.save(extension=extension, folder_name=folder_name)
            follower.save()

    except Exception as err:
        print("[FETCH_STORIES] : ", err)


def fetch_posts(follower: Follower, posts: dict):
    try:
        last_post = posts[0]['node']
        uploaded_at = datetime.fromtimestamp(last_post['taken_at_timestamp'])

        if uploaded_at <= follower.lastPost:
            return

        follower.lastPost = uploaded_at
        fetch_url = last_post['display_url']
        extension = ".jpg"
        folder_name = "/posts/" + follower.username + "/"
        new_post = Post(owner=follower, uploadedAt=uploaded_at, type=Post.PostType.POST, url=fetch_url)
        new_post.save(extension=extension, folder_name=folder_name)
        follower.save()
    except Exception as err:
        print("[FETCH_POSTS] : ", err)


# Helper functions
def valid_follower(main_user: UserInstagram, follower_user: str) -> bool:
    cookies = login_get_cookies(main_user)
    fetch_posts_url = get_posts_url(follower_user)
    session = requests.session()
    session.headers.update(get_active_headers())

    for cookie in cookies:
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    res = session.get(fetch_posts_url)
    if res.status_code >= 400:
        return False
    profile = res.json()['graphql']['user']
    if profile['followed_by_viewer'] or not profile['is_private']:
        return True
    return False

def get_posts_url(username):
    return f'https://www.instagram.com/{username}?__a=1'


def get_story_url(ID):
    return f'https://www.instagram.com/graphql/query/?query_hash=ba71ba2fcb5655e7e2f37b05aec0ff98&variables={{"reel_ids":["{ID}"],"tag_names":[],"location_ids":[],"highlight_reel_ids":[],"precomposed_overlay":false,"show_story_viewer_list":true,"story_viewer_fetch_count":50,"story_viewer_cursor":"","stories_video_dash_manifest":false}}'


def get_active_headers():
    return {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 "
            "Safari/537.36 "
    }


def get_active_cookies(user: UserInstagram) -> dict:
    current_datetime = datetime.now()
    # Assume that cookies last for 24 hours. Check it below via UserInstagram.lastActive and update if needed.
    if (current_datetime - user.lastActive).days < 1:
        return json.load(user.cookies)

    return login_get_cookies(user)

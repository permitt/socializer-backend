from datetime import datetime
import requests
from django.utils import timezone
from selenium import webdriver
from django.conf import settings
from time import sleep
import json
from insta_manager.models import UserInstagram, Friend, Post
from insta_manager.services import send_email


def initialize_scraper():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--lang=en_US')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
    driver = webdriver.Chrome(executable_path=settings.CHROME_PATH, options=options)
    return driver

def check_login(username: str, password: str) -> bool:
    driver = initialize_scraper()
    home = "https://www.instagram.com/accounts/login/"
    driver.get(home)
    sleep(3)
    user = driver.find_element_by_xpath("//*[@name='username']")
    user.send_keys(username)
    pw = driver.find_element_by_xpath("//*[@name='password']")
    pw.send_keys(password)
    sleep(2)
    # driver.find_element_by_xpath("//*[@type='submit']").click()
    driver.find_element_by_tag_name('form').submit()
    sleep(7)
    rtn = False if driver.current_url == home else True
    driver.close()
    return rtn

def login_get_cookies(user_ig: UserInstagram) -> dict:
    driver = initialize_scraper()
    driver.get("https://www.instagram.com/accounts/login/")
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
    user_ig.cookies = json.dumps(cookies)
    user_ig.save()
    return cookies

def fetch_data(username: str, *args, **kwargs):
    try:
        friend = Friend.objects.get(username=username)
    except:
        return

    numOfPosts = len(Post.objects.filter(owner=friend))
    fetch_stories_url = get_story_url(friend.user_id)
    fetch_posts_url = get_posts_url(friend.username)
    session = requests.session()
    session.headers.update(get_active_headers())

    cookies = get_active_cookies(friend.followedBy)
    for cookie in cookies:
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    res = session.get(fetch_stories_url)
    stories = res.json()['data']['reels_media']
    fetch_stories(friend, stories)
    res = session.get(fetch_posts_url)
    posts = res.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
    fetch_posts(friend, posts)

    numOfPostsNew = len(Post.objects.filter(owner=friend))
    user = args[0]
    emailNotif = args[1]
    if numOfPostsNew > numOfPosts and emailNotif:
        send_email(user, friend.username)


def fetch_stories(friend: Friend, stories: dict):
    # Check whether there are new stories
    if len(stories) == 0:
        return
    # Iterate through all stories

    try:
        for i in range(len(stories[0]['items'])):
            uploaded_at = timezone.make_aware(datetime.fromtimestamp(stories[0]['items'][i]['taken_at_timestamp']))
            if uploaded_at < friend.lastStory:
                continue

            if stories[0]['items'][i]['is_video']:
                continue
                fetch_url = stories[0]['items'][i]['video_resources'][0]['src']
                extension = "_story.mp4"
            else:
                fetch_url = stories[0]['items'][i]['display_url']
                extension = "_story.jpg"
            new_post = Post(owner=friend, uploadedAt=uploaded_at, type=Post.PostType.STORY, url=fetch_url)
            friend.lastStory = uploaded_at
            folder_name = "stories/" + friend.username + "/"
            new_post.save(extension=extension, folder_name=folder_name)
            friend.save()

    except Exception as err:
        print("[FETCH_STORIES] : ", err)


def fetch_posts(follower: Friend, posts: dict):
    try:
        last_post = posts[0]['node']
        uploaded_at = timezone.make_aware(datetime.fromtimestamp(last_post['taken_at_timestamp']))

        if uploaded_at < follower.lastPost:
            return

        follower.lastPost = uploaded_at
        fetch_url = last_post['display_url']
        extension = ".jpg"
        folder_name = "posts/" + follower.username + "/"
        new_post = Post(owner=follower, uploadedAt=uploaded_at, type=Post.PostType.POST, url=fetch_url)
        new_post.save(extension=extension, folder_name=folder_name)
        follower.save()
    except Exception as err:
        print("[FETCH_POSTS] : ", err)


# Helper functions
def valid_friend(main_user: UserInstagram, friend_user: str) -> bool:
    session = requests.session()
    session.headers.update(get_active_headers())

    cookies = get_active_cookies(main_user)
    for cookie in cookies:
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    fetch_posts_url = get_posts_url(friend_user)
    session = requests.session()
    session.headers.update(get_active_headers())

    for cookie in cookies:
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    res = session.get(fetch_posts_url)
    if res.status_code >= 400 or len(res.json().values()) == 0:
        return False, None

    profile = res.json()['graphql']['user']
    if profile['followed_by_viewer'] or not profile['is_private']:
        ret = {
            'user_id': int(profile['id']),
            'fullName': profile['full_name'],
            'picture': profile['profile_pic_url'],
        }
        return (True, ret)
    return (False, [])

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
    current_datetime = timezone.now()
    if user.cookies == '':
        return login_get_cookies(user)

    # Assume that cookies last for 24 hours. Check it below via UserInstagram.lastActive and update if needed.
    if (current_datetime - user.lastActive).days < 1:
        return json.loads(user.cookies)

    return login_get_cookies(user)

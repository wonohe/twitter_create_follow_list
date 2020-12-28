import datetime
import tweepy
import time
import json

# config
config = json.load(open('config.json', 'r'))

SCREEN_NAME = config['SCREEN_NAME']
CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']
ACCESS_TOKEN = config['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = config['ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, timeout=180, retry_delay=10, retry_count=5)

#create list
now = datetime.datetime.now()
list = api.create_list(name=f'all-{now.strftime("%Y%m%d%H%M%S")}',mode='public')
print(f'list.id:{list.id}')
print(f'list.name:{list.name}')

#add following users to list
cursor = -1
error_usr = []
while cursor != 0:
    itr = tweepy.Cursor(api.friends_ids, id=SCREEN_NAME, cursor=cursor).pages()
    try:
        for friends_ids in itr.next():
            try:
                user = api.get_user(friends_ids)
                print(user.screen_name)
                # 通信エラーユーザー対応。成功した場合は消す
                error_usr.append(user.screen_name)
                api.add_list_member(screen_name=user.screen_name, list_id=list.id, owner_screen_name=SCREEN_NAME)
                error_usr.pop()
            except tweepy.error.TweepError as e:
                print(e.reason)
    except ConnectionError as e:
        print(e)
    cursor = itr.next_cursor

print('通信エラー分対応')
# エラーがなくなるまで処理
while error_usr:
    for name in error_usr:
        try:
            print(name)
            api.add_list_member(screen_name=name, list_id=list.id, owner_screen_name=SCREEN_NAME)
            error_usr.remove(name)
        except tweepy.error.TweepError as e:
            print(e.reason)

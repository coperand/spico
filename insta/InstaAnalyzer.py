import redis
import json

class InstaAnalyzer:

    def __init__(self):
        self.red = redis.Redis()

    def handleData(self, user, key, data):
        
        bd_key = 'insta-' + user + '-' + key
        self.red.delete(bd_key)
        redis_bd_item = self.red.get(bd_key)
        
        if redis_bd_item is None:
            self.red.set(bd_key, json.dumps(data))
            return
        
        bd_data = json.loads(redis_bd_item)
        
        if key == 'private':
            self._handlePrivate(user, data, bd_data)
        elif key == 'profile':
            self._handleProfile(user, data, bd_data)
        elif key == 'followings':
            self._handleFollowings(user, data, bd_data)
        elif key == 'followers':
            self._handleFollowers(user, data, bd_data)
        elif key == 'posts':
            self._handlePosts(user, data, bd_data)
        elif key == 'stories':
            self._handleStories(user, data, bd_data)
        elif key == 'tags':
            self._handleTags(user, data, bd_data)
        elif key == 'highlihts':
            self._handleHighlights(user, data, bd_data)
        else:
            print("UNKNOWN KEY")
        
        self.red.set(bd_key, json.dumps(data))

    def _handlePrivate(self, user, data_new, data_old):
        if data_new == data_old:
            return
        if data_new == True:
            print("User @" + user + " closed account")
        else:
            print("User @" + user + " opened account")

    def _handleProfile(self, user, data_new, data_old):
        if data_new == data_old:
            return
        if data_new['name'] != data_old['name']:
            print("User @" + user + " changed name from: " + data_old['name'] + " to: " + data_new['name'])
        if data_new['bio'] != data_old['bio']:
            print("User @" + user + " changed biography from: " + data_old['bio'] + " to: " + data_new['bio'])
        if data_new['avatar_id'] != data_old['avatar_id']:
            print("User @" + user + " changed avatar to: " + data_new['avatar'])
            #TODO: Передать изображение

    def _listsDiff(self, list1, list2):
        diff1, diff2 = [], []
        for item in list1:
            if item not in list2:
                diff1.append(item)
        for item in list2:
            if item not in list1:
                diff2.append(item)
        
        return diff1, diff2

    def _handleFollowings(self, user, data_new, data_old):
        added, deleted = self._listsDiff(data_new, data_old)
        if len(added) > 0:
            send_str = 'User @' + user + ' added new followings: '
            for item in added:
                send_str += '@' + item + ' '
            print(send_str)
        if len(deleted) > 0:
            send_str = 'User @' + user + ' removed followings: '
            for item in deleted:
                send_str += '@' + item + ' '
            print(send_str)

    def _handlePosts(self, user, data_new, data_old):
        if data_new == data_old:
            return
        added, deleted = self._listsDiff(data_new, data_old)
        if len(added) > 0:
            for item in added:
                print('User @' + user + ' added new post: ' + item['id'])
        if len(deleted) > 0:
            for item in deleted:
                print('User @' + user + ' removed post: ' + item['id'])

    def _handleStories(self, user, data_new, data_old):
        if data_new == data_old:
            return

    def _handleTags(self, user, data_new, data_old):
        if data_new == data_old:
            return

    def _handleHighlights(self, user, data_new, data_old):
        if data_new == data_old:
            return

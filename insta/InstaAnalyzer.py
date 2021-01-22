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
            if key == 'stories' and data is not None:
                self._handleStories(user, data, None)
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

    def _commentsDiff(self, post1, post2):
        diff1, diff2 = [], []
        for item in post1['comments']:
            if item not in post2['comments']:
                diff1.append(item)
        
        for item in post2['comments']:
            if item not in post1['comments']:
                diff2.append(item)
        return diff1, diff2

    def _postsDiff(self, list1, list2):
        diff1 , diff2 = [], []
        comments_diff1, comments_diff2 = [], []
        for item in list1:
            found = False
            for item2 in list2:
                if item['id'] == item2['id']:
                    found = True
                    #Добавляем изменения комментариев в соответствующие списки
                    cdiff1, cdiff = self._commentsDiff(item, item2)
                    comments_diff1.append({'item': item, 'changes': cdiff1})
                    comments_diff2.append({'item': item, 'changes': cdiff2})
                    break
            if found is False:
                diff1.append(item)
        
        for item in list2:
            found = False
            for item2 in list1:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                diff2.append(item)
        
        return diff1, diff2, comments_diff1, comments_diff2

    def _handleFollowings(self, user, data_new, data_old):
        added, deleted = self._postsDiff(data_new, data_old)
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
        added, deleted, added_comments, deleted_comments = self._postDiff(data_new, data_old)
        if len(added) > 0:
            for item in added:
                print('User @' + user + ' added new post: ' + item['id'])
        if len(deleted) > 0:
            for item in deleted:
                print('User @' + user + ' removed post: ' + item['id'])
        if len(added_comments) > 0:
            for item in added_comments:
                for comment in added_comments['changes']:
                    print('User @' + user + ' has a new comment: ' + comment + ' under the post: ' + item['item']['id'])
        if len(deleted_comments) > 0:
            for item in deleted_comments:
                for comment in deleted_comments['changes']:
                    print('User @' + user + ' has lost the comment: ' + comment + ' under the post: ' + item['item']['id'])

    def _handleStories(self, user, data_new, data_old):
        if data_new is None and data_old is not None:
            return
        elif data_new is not None and data_old is None:
            for item in data_new:
                print('User @' + user + ' posted new story: ' + item['id'])
        else:
            for item in data_new:
                found = False
                for item2 in data_old:
                    if item['id'] == item2['id']:
                        found = True
                        break
                if found is False:
                    print('User @' + user + ' posted new story: ' + item['id'])

    def _tagsDiff(self, list1, list2):
        diff1 , diff2 = [], []
        for item in list1:
            found = False
            for item2 in list2:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                diff1.append(item)
        
        for item in list2:
            found = False
            for item2 in list1:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                diff2.append(item)
        
        return diff1, diff2

    def _handleTags(self, user, data_new, data_old):
        added, deleted = self._tagsDiff(data_new, data_old)
        if len(added) > 0:
            for item in added:
                print('User @' + user + ' has a new tag: ' + item['id'])
        if len(deleted) > 0:
            for item in deleted:
                print('User @' + user + ' has lost tag: ' + item['id'])

    def _handleReelMedia(self, user, highlight, stories_new, stories_old):
        for item in stories_new:
            found = False
            for item2 in stories_old:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                print('User @' + user + ' added new story: ' + item['id'] + ' to highlight: ' + highlight)
        for item in stories_old:
            found = False
            for item2 in stories_new:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                print('User @' + user + ' removed a story: ' + item['id'] + ' from highlight: ' + highlight)

    def _handleHighlights(self, user, data_new, data_old):
        for highligt in data_new:
            found = False
            for highligt_old in data_old:
                if highligt['title'] == highligt_old['title']:
                    found = True
                    #Сравнение конкретных историй
                    self._handleReelMedia(self, user, highlight['title'] ,highlight['stories'], highlight_old['stories'])
                    break
            if found is False:
                print('User @' + user + ' added new highlight: ' + highlight['title'])
                #Перебор и отправка всех новых историй
                for story in highlight['stories']:
                    print('Story: ' + story['id'])
        
        for highligt in data_old:
            found = False
            for highligt_new in data_new:
                if highligt['title'] == highligt_new['title']:
                    found = True
                    break
            if found is False:
                print('User @' + user + ' added removed highlight: ' + highlight['title'])
                #Перебор и отправка всех старых историй
                for story in highlight['stories']:
                    print('Story: ' + story['id'])


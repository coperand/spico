import json
import os
import redis

class VkAnalyzer:

    def __init__(self):
        self.red = redis.Redis()

    def handleData(self, user, uid, key, data):

        bd_key = 'vk-' + uid + '-' + key
        redis_bd_item = self.red.get(bd_key)

        if redis_bd_item is None:
            self.red.set(bd_key, json.dumps(data))
            return

        bd_data = json.loads(redis_bd_item)

        if key == 'private':
            self._handlePrivate(user, data, bd_data)
        elif key == 'profile':
            self._handleProfile(user, data, bd_data)
        elif key == 'subscriptions':
            self._handleSubscriptions(user, data, bd_data)
        elif key == 'friends':
            self._handleFriends(user, data, bd_data)
        elif key == 'videos':
            self._handleVideos(user, data, bd_data)
        elif key == 'photos':
            self._handlePhotos(user, data, bd_data)
        elif key == 'posts':
            self._handlePosts(user, data, bd_data)

        self.red.set(bd_key, json.dumps(data))

    def _removeMedia(self, media_type, media_id):
        name = '../media/vk/' + media_id + ('.jpg' if media_type == 1 else '.mp4')
        try:
            os.remove(name)
        except:
            pass

    def _handlePrivate(self, user, data_new, data_old):
        if data_new['bool'] == data_old['bool']:
            return
        if data_new['bool'] is True:
            print("User " + user + " closed account")
        else:
            print("User " + user + " opened account")

    def _handleProfile(self, user, data_new, data_old):
        if data_new == data_old:
            return
        if (data_new['first_name'] + data_new['last_name'])  != (data_old['first_name'] + data_old['last_name']):
            print("User " + user + " changed name from: " + data_old['first_name'] + ' ' + data_old['last_name'])
        if data_new['city'] != data_old['city']:
            print("User " + user + " changed city from: " + data_old['city'] + " to: " + data_new['city'])
        if data_new['status'] != data_old['status']:
            print("User " + user + " changed status from: " + data_old['status'] +  " to: " + data_new['status'])

    def _listsDiff(self, list1, list2):
        diff1, diff2 = [], []
        for item in list1:
            if item not in list2:
                diff1.append(item)
        for item in list2:
            if item not in list1:
                diff2.append(item)

        return diff1, diff2

    def _handleSubscriptions(self, user, data_new, data_old):
        added, deleted = self._listsDiff(data_new, data_old)
        if len(added) > 0:
            send_str = 'User ' + user + ' added new subscriptions: '
            for item in added:
                send_str += item + ' '
            print(send_str)
        if len(deleted) > 0:
            send_str = 'User ' + user + ' removed subscriptions: '
            for item in deleted:
                send_str += item + ' '
            print(send_str)

    def _handleFriends(self, user, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if (item['first_name'] + item['last_name'])  == (item2['first_name'] + item2['last_name']):
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has a new friend: ' + item['first_name'] + ' ' + item['last_name'] + ' (' + item['sex'] + ')')
        for item in data_old:
            found = False
            for item2 in data_new:
                if (item['first_name'] + item['last_name'])  == (item2['first_name'] + item2['last_name']):
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has lost friend: ' + item['first_name'] + ' ' + item['last_name'] + ' (' + item['sex'] + ')')

    def _handleVideos(self, user, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if item['title']  == item2['title']:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' added a new video: ' + item['title'] + ' - ' + item['url'])
        for item in data_old:
            found = False
            for item2 in data_new:
                if item['title']  == item2['title']:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' removed video: ' + item['title'] + ' - ' + item['url'])

    def _handlePhotoComments(self, user, photo, comments_new, comments_old):
        for item in comments_new:
            found = False
            for item2 in comments_old:
                if item == item2:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has a new comment: ' + item + ' under the photo - ' + photo)
        for item in comments_old:
            found = False
            for item2 in comments_new:
                if item == item2:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has losed comment: ' + item + ' under the photo - ' + photo)

    def _handlePhotosFromAlbum(self, user, album, photos_new, photos_old):
        for item in photos_new:
            found = False
            for item2 in photos_old:
                if item['id'] == item2['id']:
                    found = True
                    #Сравнение комментариев
                    self._handlePhotoComments(user, item['photo'], item['comments'], item2['comments'])
                    break
            if found is False:
                print('User ' + user + ' added new photo to album: ' + album + " - " + item['photo'])
                for comment in item['comments']:
                    print('With comment: ' + comment)
        for item in photos_old:
            found = False
            for item2 in photos_new:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' removed photo from album: ' + album + " - " + item['photo'])
                self._removeMedia(1, str(item['id']))
                for comment in item['comments']:
                    print('With comment: ' + comment)

    def _handlePhotos(self, user, data_new, data_old):
        for album in data_new:
            found = False
            for album_old in data_old:
                if album['title'] == album_old['title']:
                    found = True
                    #Сравнение конкретных фотографий
                    self._handlePhotosFromAlbum(user, album['title'] ,album['items'], album_old['items'])
                    break
            if found is False:
                print('User ' + user + ' added new album: ' + album['title'])
                #Перебор и отправка всех новых фотографий
                for photo in album['items']:
                    print('Photo - ' + photo['photo'])
                    for comment in photo['comments']:
                        print('With comment: ' + comment)

        for album in data_old:
            found = False
            for album_new in data_new:
                if album['title'] == album_new['title']:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' added removed album: ' + album['title'])
                #Перебор и отправка всех старых фотографий
                for photo in album['items']:
                    print('Photo - ' + photo['photo'])
                    for comment in photo['comments']:
                        print('With comment: ' + comment)
                    self._removeMedia(1, str(photo['id']))

    def _handlePostComments(self, user, post, comments_new, comments_old):
        for item in comments_new:
            found = False
            for item2 in comments_old:
                if item == item2:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has a new comment under the post: ' + post + " - " + item)
        for item in comments_old:
            found = False
            for item2 in comments_new:
                if item == item2:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' has losed comment under the post: ' + post + " - " + item)

    def _handlePosts(self, user, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if item['id']  == item2['id']:
                    found = True
                    #Сравнение комментов
                    self._handlePostComments(user, item['text'], item['comments'], item2['comments'])
                    break
            if found is False:
                print('User ' + user + ' added a new post: ' + item['text'])
                for photo in item['attachments']:
                    print('With photo - ' + photo['photo'])
                    for comment in item['comments']:
                        print('With comment: ' + comment)
        for item in data_old:
            found = False
            for item2 in data_new:
                if item['id']  == item2['id']:
                    found = True
                    break
            if found is False:
                print('User ' + user + ' removed post: ' + item['text'])
                for photo in item['attachments']:
                    print('With photo - ' + photo['photo'])
                    self._removeMedia(1, str(photo['id']))
                for comment in item['comments']:
                    print('With comment: ' + comment)

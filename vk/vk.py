import urllib.request
import os.path
import vk_api
from vk.VkAnalyzer import VkAnalyzer

class VkModule:

    def __init__(self, phone, passwd):
        '''Подготовка клиента'''
        vk_session = vk_api.VkApi(phone, passwd)
        vk_session.auth()
        self.vk = vk_session.get_api()
        #TODO: Обработка исключения в вызывающем коде

        self.analyzer = VkAnalyzer()

    def getData(self, targetId):

        #Получаем информацию о пользователе и проверяем аккаунт на закрытость
        ret = self._receiveUserInfo(targetId)
        username = ret['first_name'] + ' ' + ret['last_name']
        if ret['is_closed'] is True:
            self.analyzer.handleData(username, targetId, 'private', {'bool': True})
            return
        else:
            self.analyzer.handleData(username, targetId, 'private', {'bool': False})

        self.analyzer.handleData(username, targetId, 'profile', ret)

        #Получаем подписки и группы
        self.analyzer.handleData(username, targetId, 'subscriptions', self._receiveAllSubscriptions(targetId))

        #Получаем друзей
        self.analyzer.handleData(username, targetId, 'friends', self._receiveFriends(targetId))

        #Получаем видео
        self.analyzer.handleData(username, targetId, 'videos', self._receiveVideos(targetId))

        #Получаем фотографии(с комментариями)
        self.analyzer.handleData(username, targetId, 'photos', self._receiveAllPhotos(targetId))

        #Получаем записи на стене (с комментариями)
        self.analyzer.handleData(username, targetId, 'posts', self._receivePosts(targetId))

    def _saveMedia(self, media_type, media_id, url):
        name = 'media/vk/' + str(media_id) + ('.jpg' if media_type == 1 else '.mp4')
        #Проверка наличия файла с таким именем
        if os.path.exists(name):
            return

        img = urllib.request.urlopen(url).read()
        out = open(name, "wb")
        out.write(img)
        out.close()

    def _receiveUserInfo(self, targetId):
        response = self.vk.users.get(user_ids=targetId, fields='''sex, bdate, city, home_town, online, contacts, site, education, universities, schools, status, last_seen, followers_count, occupation, relatives, relation, personal,
        connections, exports, activities, interests, music, movies, tv, books, games, about, quotes, career''')[0]
        ret = {}

        ret['is_closed'] = response['is_closed']
        ret['first_name'] = response['first_name']
        ret['last_name'] = response['last_name']
        ret['city'] = response.setdefault('city', '')
        if ret['city'] != '':
            ret['city'] = response['city']['title']
        ret['status'] = response['status']
        return ret

    def _receiveSubscriptions(self, targetId):
        subscriptions = []
        offset = 0
        while True:
            response = self.vk.users.getSubscriptions(user_id=targetId,  count=200, offset=offset, extended=1)
            subscriptions.extend(response['items'])
            if len(response['items']) < 200:
                break
            offset += 200

        result = []
        for item in subscriptions:
            if item['type'] == 'page':
                result.append(item['name'])
            elif item['type'] == 'profile':
                result.append(item['first_name'] + ' ' + item['last_name'])
            else:
                result.append(item + " - UNKNOWN TYPE")
        return result

    def _receiveGroups(self, targetId):
        groups = []
        offset = 0
        while True:
            response = self.vk.groups.get(user_id=targetId, count=1000, offset=offset, extended=1)
            groups.extend(response['items'])
            if len(response['items']) < 1000:
                break
            offset += 1000

        result = []
        for item in groups:
            result.append(item['name'])

        return result

    def _receiveAllSubscriptions(self, targetId):
        x = self._receiveSubscriptions(targetId)
        y = self._receiveGroups(targetId)
        diff = list(set(y).difference(set(x)))
        x.extend(diff)

        ret = []
        for item in x:
            ret.append(item)
        return ret

    def _receiveFriends(self, targetId):
        friends = []
        offset = 0
        while True:
            response = self.vk.friends.get(user_id=targetId, count=5000, offset=offset, fields='sex, city')
            friends.extend(response['items'])
            if len(response['items']) < 5000:
                break
            offset += 5000

        ret = []
        for item in friends:
            ret.append({'first_name': item['first_name'], 'last_name': item['last_name'], 'sex': "M" if item['sex'] == 2 else "F"})
        return ret

    def _receiveVideos(self, targetId):
        videos = []
        offset = 0
        while True:
            response = self.vk.video.get(owner_id=targetId, count=100, offset=offset)
            videos.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        ret = []
        for item in videos:
            ret.append({'title': item['title'], 'url': item.setdefault('player', '')})
        return ret

    def _receivePhotoComments(self, targetId, photoId):
        comments = []
        offset = 0
        while True:
            response = self.vk.photos.getComments(owner_id=targetId, count=100, offset=offset, photo_id=photoId)
            comments.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        ret = []
        for item in comments:
            ret.append(item['text'])
        return ret

    def _receiveAlbums(self, targetId):
        albums = []
        offset = 0
        while True:
            response = self.vk.photos.getAlbums(owner_id=targetId, count=100, offset=offset, need_system=1)
            albums.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        return albums

    def _receiveAlbumItems(self, targetId, albumId):
        photos = []
        offset = 0
        while True:
            response = self.vk.photos.get(owner_id=targetId, count=100, extended=1, offset=offset, album_id=albumId)
            photos.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        ret = []
        for item in photos:
            ret_item = {}
            ret_item['id'] = item['id']
            ret_item['photo'] = item['sizes'][-1]['url']
            self._saveMedia(1, ret_item['id'], ret_item['photo'])
            if item['comments']['count'] > 0:
                ret_item['comments'] = self._receivePhotoComments(targetId, item['id'])
            else:
                ret_item['comments'] = []
            ret.append(ret_item)
        return ret

    def _receiveAllPhotos(self, targetId):
        albums = self._receiveAlbums(targetId)

        ret = []
        for album in albums:
            ret.append({'title': album['title'], 'items': self._receiveAlbumItems(targetId, album['id'])})
        return ret

    def _receivePostComments(self, targetId, postId):
        comments = []
        offset = 0
        while True:
            response = self.vk.wall.getComments(owner_id=targetId, count=100, offset=offset, post_id=postId)
            comments.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        ret = []
        for item in comments:
            ret.append(item['text'])
        return ret

    def _receivePosts(self, targetId):
        posts = []
        offset = 0
        while True:
            response = self.vk.wall.get(owner_id=targetId, count=100, offset=offset)
            posts.extend(response['items'])
            if len(response['items']) < 100:
                break
            offset += 100

        ret = []
        for item in posts:
            ret_item = {}
            ret_item['text'] = item['text']
            ret_item['id'] = item['id']
            ret_item['attachments'] = []
            for attachment in item.setdefault('attachments', []):
                if attachment['type'] == 'photo':
                    ret_item['attachments'].append({'id': attachment['photo']['id'], 'photo': attachment['photo']['sizes'][-1]['url']})
                    self._saveMedia(1, attachment['photo']['id'], attachment['photo']['sizes'][-1]['url'])
            if item['comments']['count'] > 0:
                ret_item['comments'] = self._receivePostComments(targetId, item['id'])
            else:
                ret_item['comments'] = []
            ret.append(ret_item)
        return ret

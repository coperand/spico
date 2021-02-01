import time
import insta.InstagramAPI as iAPI
from insta.InstaAnalyzer import InstaAnalyzer

class InstaModule:

    def __init__(self, login, passwd, callback):
        '''Подготовка клиента и класса для анализа данных'''
        self.client = iAPI.InstagramAPI(login, passwd)
        self.client.login()
        if self.client.isLoggedIn is False:
            raise Exception("Instagram logging failure")
        self.analyzer = InstaAnalyzer(callback)

    def checkName(self, nickname):
        if self._getUserId(nickname) is False:
            return False
        else:
            return True

    def removeData(self, nickname):
        self.analyzer.removeUser(nickname)

    def getData(self, nickname, chatId):

        #Получение идентификатора пользователя по имени
        targetId = self._getUserId(nickname)

        #Получение информации об аккаунте и возврат в случае, если он закрытый
        ret = self._receiveProfileInfo(targetId)
        if ret is False:
            self.analyzer.handleData(nickname, chatId, 'private', {'bool': True})
            return
        else:
            self.analyzer.handleData(nickname, chatId, 'private', {'bool': False})

        self.analyzer.handleData(nickname, chatId, 'profile', ret)
        time.sleep(1)

        #Получение подписок
        self.analyzer.handleData(nickname, chatId, 'followings', self._receiveFollowings(targetId))
        time.sleep(1)

        #Получение публикаций (с комментариями)
        self.analyzer.handleData(nickname, chatId, 'posts', self._receivePosts(targetId))
        time.sleep(1)

        #Получение историй
        stories = self._receiveStories(targetId)
        if stories is not False:
            self.analyzer.handleData(nickname, chatId, 'stories', stories)
        else:
            self.analyzer.handleData(nickname, chatId, 'stories', None)
        time.sleep(1)

        #Получение фото, на которых отмечен пользователь
        self.analyzer.handleData(nickname,  chatId,'tags', self._receiveUserTags(targetId))
        time.sleep(1)

        #Получение всех историй из панели актуального
        self.analyzer.handleData(nickname, chatId, 'highlights', self._receiveHighlights(targetId))

    def _getUserId(self, username):
        '''Получаем id пользователя по имени'''
        result = self.client.getTotalSearchUsername(username)
        if result is False:
            return False
        else:
            return result['pk']

    def _receiveProfileInfo(self, targetId):
        '''Получаем информацию об аккаунте'''
        profile = self.client.getTotalUsernameInfo(targetId)
        ret = {}

        if profile['is_private'] is True:
            return False

        ret['name'] = profile['full_name']
        ret['bio'] = profile['biography']
        ret['avatar'] = profile['hd_profile_pic_url_info']['url']
        ret['avatar_id'] = profile['profile_pic_id']
        return ret

    def _receiveFollowings(self, targetId):
        '''Получаем подписки'''
        followings = self.client.getTotalFollowings(targetId)
        ret = []

        for item in followings:
            ret.append(item['username'])
        return ret

    def _receiveComments(self, mediaId):
        '''Получаем комментарии к посту'''
        comments = self.client.getTotalMediaComments(mediaId)
        ret = []

        for item in comments:
            ret.append({'user': item['user']['username'], 'text': item['text']})
        return ret

    def _receivePosts(self, targetId):
        '''Получаем все посты пользователя'''
        posts = self.client.getTotalUserFeed(targetId)
        ret = []

        for item in posts:
            ret_item = {}

            if item['media_type'] == 1:
                ret_item['type'] = 1
                ret_item['id'] = item['id']
                ret_item['photo'] = item['image_versions2']['candidates'][0]['url']
            elif item['media_type'] == 2:
                ret_item['type'] = 2
                ret_item['id'] = item['id']
                ret_item['video'] = item['video_versions'][0]['url']
            elif item['media_type'] == 8:
                ret_item['type'] = 8
                ret_item['id'] = item['id']
                ret_item['carousel'] = []

                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]

                    if media['media_type'] == 1:
                        ret_item['carousel'].append({'type': 1, 'id': media['id'], 'photo': media['image_versions2']['candidates'][0]['url']})
                    elif media['media_type'] == 2:
                        ret_item['carousel'].append({'type': 2, 'id': media['id'], 'video': media['video_versions'][0]['url']})

            if item['comment_count'] > 0:
                ret_item['comments'] = self._receiveComments(item['id'])
            else:
                ret_item['comments'] = []
            ret.append(ret_item)

        return ret

    def _receiveStories(self, targetId):
        '''Получаем текущие истории'''
        stories = self.client.getTotalStory(targetId)
        ret = []

        if stories['latest_reel_media'] is None:
            return False

        for item in stories['items']:
            if item['media_type'] == 1:
                ret.append({'type': 1, 'id': item['id'], 'photo': item['image_versions2']['candidates'][0]['url']})
            elif item['media_type'] == 2:
                ret.append({'type': 2, 'id': item['id'], 'video': item['video_versions'][0]['url']})
        return ret

    def _receiveUserTags(self, targetId):
        '''Получаем посты, на которых отметили пользователя'''
        tags = self.client.getTotalUserTags(targetId)
        ret = []

        for item in tags:
            ret_item = {}

            if item['media_type'] == 1:
                ret_item['type'] = 1
                ret_item['id'] = item['id']
                ret_item['photo'] = item['image_versions2']['candidates'][0]['url']
            elif item['media_type'] == 2:
                ret_item['type'] = 2
                ret_item['id'] = item['id']
                ret_item['video'] = item['video_versions'][0]['url']
            elif item['media_type'] == 8:
                ret_item['type'] = 8
                ret_item['id'] = item['id']
                ret_item['carousel'] = []

                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]

                    if media['media_type'] == 1:
                        ret_item['carousel'].append({'type': 1, 'id': media['id'], 'photo': media['image_versions2']['candidates'][0]['url']})
                    elif media['media_type'] == 2:
                        ret_item['carousel'].append({'type': 2, 'id': media['id'], 'video': media['video_versions'][0]['url']})
            ret.append(ret_item)
        return ret

    def _receiveReelMedia(self, reelId):
        '''Получаем конкретные истории из актуального'''
        medias = self.client.getTotalReelMedia(reelId)
        ret = []

        for item in medias:
            if item['media_type'] == 1:
                ret.append({'type': 1, 'id': item['id'], 'photo': item['image_versions2']['candidates'][0]['url']})
            elif item['media_type'] == 2:
                ret.append({'type': 2, 'id': item['id'], 'video': item['video_versions'][0]['url']})
        return ret

    def _receiveHighlights(self, targetId):
        '''Получаем наборы историй с панели актуального'''
        highlights = self.client.getTotalUserHighlights(targetId)
        ret = []

        for item in highlights:
            ret.append({'title': item['title'], 'stories': self._receiveReelMedia(item['id'])})
            time.sleep(1)
        return ret

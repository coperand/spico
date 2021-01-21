import InstagramAPI as iAPI
import urllib.request
import os.path


class InstaModule:

    def __init__(self, login, passwd):
        '''Подготовка клиента'''
        self.client = iAPI.InstagramAPI(login, passwd)
        self.client.login()
        if self.client.isLoggedIn is False:
            raise Exception("Instagram logging failure")
        #TODO: Обработка исключения в вызывающем коде

    def getData(self, nickname):
        
        #Получение идентификатора пользователя по имени
        targetId = self.getUserId(nickname)
        
        #TODO: Проверка корректности имени на стадии его добавления
        
        #Получение информации об аккаунте и возврат в случае, если он закрытый
        ret = self._receiveProfileInfo(targetId)
        if ret is False:
            #TODO: Оповестить о закрытости аккаунта
            return
        #print(ret)
        
        #Получение подписок
        #ret = self._receiveFollowings(targetId)
        #print(ret)
        
        #Получение подписчиков
        #ret = self._receiveFollowers(targetId)
        #print(ret)
        
        #Получение публикаций (с комментариями)
        #ret = self._receivePosts(targetId)
        #print(ret)
        
        #Получение историй
        #ret = self._receiveStories(targetId)
        #if ret is not False:
        #    #TODO: Оповещение об истории
        #    print(ret)
        
        #Получение фото, на которых отмечен пользователь
        #ret = self._receiveUserTags(targetId)
        #print(ret)
        
        #Получение всех историй из панели актуального
        #ret = self._receiveHighlights(targetId)
        #print(ret)
    
    def _saveMedia(self, media_type, media_id, url):
        name = '../media/insta/' + media_id + ('.jpg' if media_type == 1 else '.mp4')
        #Проверка наличия файла с таким именем
        if os.path.exists(name):
            return
        
        img = urllib.request.urlopen(url).read()
        out = open(name, "wb")
        out.write(img)
        out.close()
    
    def getUserId(self, username):
        '''Получаем id пользователя по имени'''
        return self.client.getTotalSearchUsername(username)['pk']

    def _receiveProfileInfo(self, targetId):
        '''Получаем информацию об аккаунте'''
        profile = self.client.getTotalUsernameInfo(targetId)
        ret = {}
        
        if profile['is_private'] == True:
            print("Account is private")
            return False
        
        ret['name'] = profile['full_name']
        ret['bio'] = profile['biography']
        ret['avatar'] = profile['hd_profile_pic_url_info']['url']
        ret['avatar_id'] = profile['profile_pic_id']
        self._saveMedia(1, ret['avatar_id'], ret['avatar'])
        return ret

    def _receiveFollowings(self, targetId):
        '''Получаем подписки'''
        followings = self.client.getTotalFollowings(targetId)
        ret = []
        
        for item in followings:
            ret.append(item['username'])
        return ret

    def _receiveFollowers(self, targetId):
        '''Получаем подписки'''
        followers = self.client.getTotalFollowers(targetId)
        ret = []
        
        for item in followers:
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
                self._saveMedia(1, ret_item['id'], ret_item['photo'])
            elif item['media_type'] == 2:
                ret_item['type'] = 2
                ret_item['id'] = item['id']
                ret_item['video'] = item['video_versions'][0]['url']
                self._saveMedia(2, ret_item['id'], ret_item['video'])
            elif item['media_type'] == 8:
                ret_item['type'] = 8
                ret_item['carousel'] = []
                
                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]
                    
                    if media['media_type'] == 1:
                        ret_item['carousel'].append({'type': 1, 'id': media['id'], 'photo': media['image_versions2']['candidates'][0]['url']})
                        self._saveMedia(1, ret_item['carousel'][-1]['id'], ret_item['carousel'][-1]['photo'])
                    elif media['media_type'] == 2:
                        ret_item['carousel'].append({'type': 2, 'id': media['id'], 'video': media['video_versions'][0]['url']})
                        self._saveMedia(2, ret_item['carousel'][-1]['id'], ret_item['carousel'][-1]['video'])
            
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
        
        if stories['latest_reel_media'] == None:
            return False
        
        print("Stories:")
        for item in stories['items']:
            if item['media_type'] == 1:
                ret.append({'type': 1, 'id': item['id'], 'photo': item['image_versions2']['candidates'][0]['url']})
                self._saveMedia(1, ret[-1]['id'], ret[-1]['photo'])
            elif item['media_type'] == 2:
                ret.append({'type': 2, 'id': item['id'], 'video': item['video_versions'][0]['url']})
                self._saveMedia(2, ret[-1]['id'], ret[-1]['video'])
        return ret

    def _receiveUserTags(self, targetId):
        '''Получаем истории, на которых отметили пользователя'''
        tags = self.client.getTotalUserTags(targetId)
        ret = []
        
        for item in tags:
            ret_item = {}
            
            if item['media_type'] == 1:
                ret_item['type'] = 1
                ret_item['id'] = item['id']
                ret_item['photo'] = item['image_versions2']['candidates'][0]['url']
                self._saveMedia(1, ret_item['id'], ret_item['photo'])
            elif item['media_type'] == 2:
                ret_item['type'] = 2
                ret_item['id'] = item['id']
                ret_item['video'] = item['video_versions'][0]['url']
                self._saveMedia(2, ret_item['id'], ret_item['video'])
            elif item['media_type'] == 8:
                ret_item['type'] = 8
                ret_item['carousel'] = []
                
                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]
                    
                    if media['media_type'] == 1:
                        ret_item['carousel'].append({'type': 1, 'id': media['id'], 'photo': media['image_versions2']['candidates'][0]['url']})
                        self._saveMedia(1, ret_item['carousel'][-1]['id'], ret_item['carousel'][-1]['photo'])
                    elif media['media_type'] == 2:
                        ret_item['carousel'].append({'type': 2, 'id': media['id'], 'video': media['video_versions'][0]['url']})
                        self._saveMedia(2, ret_item['carousel'][-1]['id'], ret_item['carousel'][-1]['video'])
            ret.append(ret_item)
        return ret
    
    def _receiveReelMedia(self, reelId):
        '''Получаем конкретные истории из актуального'''
        medias = self.client.getTotalReelMedia(reelId)
        ret = []
        
        for item in medias:
            if item['media_type'] == 1:
                ret.append({'type': 1, 'id': item['id'], 'photo': item['image_versions2']['candidates'][0]['url']})
                self._saveMedia(1, ret[-1]['id'], ret[-1]['photo'])
            elif item['media_type'] == 2:
                ret.append({'type': 2, 'id': item['id'], 'video': item['video_versions'][0]['url']})
                self._saveMedia(2, ret[-1]['id'], ret[-1]['video'])
        return ret

    def _receiveHighlights(self, targetId):
        '''Получаем наборы историй с панели актуального'''
        highlights = self.client.getTotalUserHighlights(targetId)
        ret = []
        
        for item in highlights:
            ret.append({'title': item['title'], 'stories': self._receiveReelMedia(item['id'])})
        return ret

insta = InstaModule('ingabeiko94', 'mKzkgUbYBs')
insta.getData("arina_weasley")

import InstagramAPI as iAPI


class InstaModule:

    def __init__(self, login, passwd):
        '''Подготовка клиента'''
        self.client = iAPI.InstagramAPI(login, passwd)
        self.client.login()

    def getData(self, nickname):
        
        #Получение идентификатора пользователя по имени
        targetId = self.getUserId(nickname)
        
        #TODO: Сначала получить информацию об аккаунте и проверить его на закрытость
        #TODO: Переименовать методы с  print на другое после изменения семантики
        
        #Получить подписки
        #self._printFollowings(targetId)
        
        #Получить подписчиков
        #self._printFollowers(targetId)
        
        #Получить публикации (с комментариями)
        #self._printPosts(targetId)
        
        #Получить информацию об аккаунте
        #self._printProfileInfo(targetId)
        
        #Получить истории
        #self._printStories(targetId)
        
        #Получить фото, на которых отмечен пользователь
        #self._printUserTags(targetId)
        
        #Получить все истории из панели актуального
        #self._printHighlights(targetId)

    def getUserId(self, username):
        '''Получаем id пользователя по имени'''
        return self.client.getTotalSearchUsername(username)['pk']

    def _printFollowings(self, targetId):
        '''Получаем подписки'''
        followings = self.client.getTotalFollowings(targetId)
        
        for item in followings:
            print(item['username'])
        
        print("Summary:", len(followings))

    def _printFollowers(self, targetId):
        '''Получаем подписки'''
        followers = self.client.getTotalFollowers(targetId)
        
        for item in followers:
            print(item['username'])
        
        print("Summary:", len(followers))

    def _printComments(self, mediaId):
        '''Получаем комментарии к посту'''
        comments = self.client.getTotalMediaComments(mediaId)
        print("Comments:")
        for item in comments:
            print("= @", item['user']['username'], ": ",  item['text'], sep='')

    def _printPosts(self, targetId):
        '''Получаем все посты пользователя'''
        posts = self.client.getTotalUserFeed(targetId)
        
        for item in posts:
            if item['media_type'] == 1:
                print("id:", item['id'], 'photo_url:', item['image_versions2']['candidates'][0]['url'])
            elif item['media_type'] == 2:
                print("id:", item['id'], 'video_url:', item['video_versions'][0]['url'])
            elif item['media_type'] == 8:
                print("Carousel:")
                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]
                    
                    if media['media_type'] == 1:
                        print("", i + 1, "-", "id:", media['id'], 'photo_url:', media['image_versions2']['candidates'][0]['url'])
                    elif media['media_type'] == 2:
                        print("", i + 1, "-", "id:", media['id'], 'video_url:', media['video_versions'][0]['url'])
                    else:
                        print("", i + 1, "-", "id:", media['id'], "media_type:", media['media_type'], "MEDIA TYPE IS UNKNOWN!")
            else:
                print("id:", item['id'], "media_type:", item['media_type'], "MEDIA TYPE IS UNKNOWN!")
            
            if item['comment_count'] > 0:
                self._printComments(item['id'])
            print()
        
        print("Summary:", len(posts))

    def _printProfileInfo(self, targetId):
        '''Получаем информацию об аккаунте'''
        profile = self.client.getTotalUsernameInfo(targetId)
        if profile['is_private'] == True:
            print("Account is private")
            return
        
        print("Fullname:", profile['full_name'])
        print("Biography:", profile['biography'])
        print("Profile pic url:", profile['hd_profile_pic_url_info']['url'])

    def _printStories(self, targetId):
        '''Получаем текущие истории'''
        stories = self.client.getTotalStory(targetId)
        
        if stories['latest_reel_media'] == None:
            print("There is no stories media")
            return
        
        print("Stories:")
        for item in stories['items']:
            if item['media_type'] == 1:
                print('photo_url:', item['image_versions2']['candidates'][0]['url'])
            elif item['media_type'] == 2:
                print('video_url:', item['video_versions'][0]['url'])
            else:
                print("id:", item['id'], "media_type:", item['media_type'], "MEDIA TYPE IS UNKNOWN!")
        
        print("Summary:", len(stories['items']))

    def _printUserTags(self, targetId):
        '''Получаем истории, на которых отметили пользователя'''
        tags = self.client.getTotalUserTags(targetId)
        
        for item in tags:
            if item['media_type'] == 1:
                print("id:", item['id'], 'photo_url:', item['image_versions2']['candidates'][0]['url'])
            elif item['media_type'] == 2:
                print("id:", item['id'], 'video_url:', item['video_versions'][0]['url'])
            elif item['media_type'] == 8:
                print("Carousel:")
                for i in range(0, item['carousel_media_count']):
                    media = item['carousel_media'][i]
                    
                    if media['media_type'] == 1:
                        print("", i + 1, "-", "id:", media['id'], 'photo_url:', media['image_versions2']['candidates'][0]['url'])
                    elif media['media_type'] == 2:
                        print("", i + 1, "-", "id:", media['id'], 'video_url:', media['video_versions'][0]['url'])
                    else:
                        print("", i + 1, "-", "id:", media['id'], "media_type:", media['media_type'], "MEDIA TYPE IS UNKNOWN!")
            else:
                print("id:", item['id'], "media_type:", item['media_type'], "MEDIA TYPE IS UNKNOWN!")
            
            print()
        
        print("Summary:", len(tags))
    
    def _printReelMedia(self, reelId):
        '''Получаем конкретные истории из актуального'''
        medias = self.client.getTotalReelMedia(reelId)
        
        for item in medias:
            if item['media_type'] == 1:
                print("id:", item['id'], 'photo_url:', item['image_versions2']['candidates'][0]['url'])
            elif item['media_type'] == 2:
                print("id:", item['id'], 'video_url:', item['video_versions'][0]['url'])
            else:
                print("id:", item['id'], "media_type:", item['media_type'], "MEDIA TYPE IS UNKNOWN!")

    def _printHighlights(self, targetId):
        '''Получаем наборы историй с панели актуального'''
        highlights = self.client.getTotalUserHighlights(targetId)
        
        for item in highlights:
            print(item['title'], ":", sep='')
            self._printReelMedia(item['id'])
            print()


insta = InstaModule('ingabeiko94', 'mKzkgUbYBs')
insta.getData("arina_weasley")

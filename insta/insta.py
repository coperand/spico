import InstagramAPI as iAPI


def getUserId(client, username):
    return client.getTotalSearchUsername(username)['pk']

def printFollowings(client, targetId):
    followings = client.getTotalFollowings(targetId)
    
    for item in followings:
        print(item['username'])
    
    print("Summary:", len(followings))


def printFollowers(client, targetId):
    followers = client.getTotalFollowers(targetId)
    
    for item in followers:
        print(item['username'])
    
    print("Summary:", len(followers))


def printComments(client, mediaId):
    comments = client.getTotalMediaComments(mediaId)
    print("Comments:")
    for item in comments:
        print("= @", item['user']['username'], ": ",  item['text'], sep='')


def printPosts(client, targetId):
    posts = client.getTotalUserFeed(targetId)
    
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
            printComments(client, item['id'])
        print()
    
    print("Summary:", len(posts))


def printProfileInfo(client, targetId):
    profile = client.getTotalUsernameInfo(targetId)
    if profile['is_private'] == True:
        print("Account is private")
        return
    
    print("Fullname:", profile['full_name'])
    print("Biography:", profile['biography'])
    print("Profile pic url:", profile['hd_profile_pic_url_info']['url'])


def printStories(client, targetId):
    stories = client.getTotalStory(targetId)
    
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

def printUserTags(client, targetId):
    tags = client.getTotalUserTags(targetId)
    
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


#Подготовка клиента
client = iAPI.InstagramAPI('ingabeiko94', 'mKzkgUbYBs')
client.login()

#Получение идентификатора пользователя по имени
targetId = getUserId(client, "arina_weasley")

#Получить подписки
#printFollowings(client, targetId)

#Получить подписчиков
#printFollowers(client, targetId)

#Получить публикации (с комментариями)
#printPosts(client, targetId)

#Получить информацию об аккаунте
#printProfileInfo(client, targetId)

#Получить истории
#printStories(client, targetId)

#Получить фото, на которых отмечен пользователь
#printUserTags(client, targetId)

#client.getUserHighlights(targetId)
#print(client.LastJson)

client.getReelMedia("highlight:17943492508091954")
print(client.LastJson)

import vk_api

accountPhone = '8801923291704'
accountPass = 'CM8Ipp69w'

targetId = '78961353'
myId = '85974301'

vk_session = vk_api.VkApi(accountPhone, accountPass)
vk_session.auth()

vk = vk_session.get_api()

def printUserInfo(vk, targetId):
    response = vk.users.get(user_ids=targetId, fields='''sex, bdate, city, home_town, online, contacts, site, education, universities, schools, status, last_seen, followers_count, occupation, relatives, relation, personal,
     connections, exports, activities, interests, music, movies, tv, books, games, about, quotes, career''')[0]
    
    if response['is_closed'] == True:
        print("Account is closed")
        return
    
    print("First name:", response['first_name'], "Last name:", response['last_name'], "City:",  response.setdefault('city', 'None'), "Status:",  response.setdefault('status', 'None'),
    "Contacts:",  response.setdefault('contacts', 'None'), "Site:",  response['site'], "Relatives:",  response.setdefault('relatives', 'None'), "Relation:",  response.setdefault('relation', 'None'))

def printPostComments(vk, targetId, postId):
    comments = []
    offset = 0
    while True:
        response = vk.wall.getComments(owner_id=targetId, count=100, offset=offset, post_id=postId)
        comments.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    for item in comments:
        print("= Comment:", item['text'])

def printPosts(vk, targetId):
    posts = []
    offset = 0
    while True:
        response = vk.wall.get(owner_id=targetId, count=100, offset=offset)
        posts.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    for item in posts:
        print("Text:", item['text'])
        for attachment in item.setdefault('attachments', []):
            if attachment['type'] == 'photo':
                print("= Photo url:", attachment['photo']['sizes'][-1]['url'])
        if item['comments']['count'] > 0:
            printPostComments(vk, targetId, item['id'])
    
    print("Summary:", len(posts))

def printPhotoComments(vk, targetId, photoId):
    comments = []
    offset = 0
    while True:
        response = vk.photos.getComments(owner_id=targetId, count=100, offset=offset, photo_id=photoId)
        comments.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    for item in comments:
        print("= Comment:", item['text'])

def getAlbums(vk, targetId):
    albums = []
    offset = 0
    while True:
        response = vk.photos.getAlbums(owner_id=targetId, count=100, offset=offset, need_system=1)
        albums.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    return albums

def printAlbum(vk, targetId, albumId):
    photos = []
    offset = 0
    while True:
        response = vk.photos.get(owner_id=targetId, count=100, extended=1, offset=offset, album_id=albumId)
        photos.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    for item in photos:
        print(item['sizes'][-1]['url'])
        if item['comments']['count'] > 0:
            printPhotoComments(vk, targetId, item['id'])

def printPhotos(vk, targetId):
    albums = getAlbums(vk, targetId)
    
    for album in albums:
        print('Album "', album['title'], '":', sep='')
        printAlbum(vk, targetId, album['id'])
        print()

def printVideos(vk, targetId):
    videos = []
    offset = 0
    while True:
        response = vk.video.get(owner_id=targetId, count=100, offset=offset)
        videos.extend(response['items'])
        if(len(response['items']) < 100):
            break
        offset += 100
    
    for item in videos:
        print(item['title'], "-", item['player'])
    print("Summary:", len(videos))

def getSubscriptions(vk, targetId):
    subscriptions = []
    offset = 0
    while True:
        response = vk.users.getSubscriptions(user_id=targetId,  count=200, offset=offset, extended=1)
        subscriptions.extend(response['items'])
        if(len(response['items']) < 200):
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

def getGroups(vk, targetId):
    groups = []
    offset = 0
    while True:
        response = vk.groups.get(user_id=targetId, count=1000, offset=offset, extended=1)
        groups.extend(response['items'])
        if(len(response['items']) < 1000):
            break
        offset += 1000
    
    result = []
    for item in groups:
        result.append(item['name'])
    
    return result

def printSubscriptions(vk, targetId):
    x = getSubscriptions(vk, targetId)
    y = getGroups(vk, targetId)
    diff = list(set(y).difference(set(x)))
    x.extend(diff)
    
    for item in x:
        print(item)
    print("Summary:", len(x))

def printFriends(vk, targetId):
    friends = []
    offset = 0
    while True:
        response = vk.friends.get(user_id=targetId, count=5000, offset=offset, fields='sex, city')
        friends.extend(response['items'])
        if(len(response['items']) < 5000):
            break
        offset += 5000
    
    for item in friends:
        print(item['first_name'], item['last_name'], "(М)" if item['sex'] == 2 else "(Ж)")
    print("Summary:", len(friends))

#TODO: Сначала проверка на закрытость аккаунта, затем все остальное

#Получаем фотографии(с комментариями)
printPhotos(vk, targetId)

#Получаем записи на стене (с комментариями)
#printPosts(vk, targetId)

#Получаем видео
#printVideos(vk, targetId)

#Получаем подписки и группы
#printSubscriptions(vk, targetId)

#Получаем группы
#printGroups(vk, targetId)

#Получаем друзей
#printFriends(vk, targetId)

#Получаем информацию о пользователе
#printUserInfo(vk, targetId)

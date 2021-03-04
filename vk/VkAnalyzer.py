import json
import redis

class VkAnalyzer:

    def __init__(self, callback):
        self.callback = callback
        self.red = redis.Redis()

    def removeUser(self, user):
        keys = ['private', 'profile', 'subscriptions', 'friends', 'videos', 'photos', 'posts']
        for key in keys:
            bd_key = 'vk-' + user + '-' + key
            self.red.delete(bd_key)

    def handleData(self, user, uid, chatId, key, data):

        bd_key = 'vk-' + uid + '-' + key
        redis_bd_item = self.red.get(bd_key)

        if redis_bd_item is None:
            self.red.set(bd_key, json.dumps(data))
            return

        bd_data = json.loads(redis_bd_item)

        if key == 'private':
            self._handlePrivate(user, uid, chatId, data, bd_data)
        elif key == 'profile':
            self._handleProfile(user, uid, chatId, data, bd_data)
        elif key == 'subscriptions':
            self._handleSubscriptions(user, uid, chatId, data, bd_data)
        elif key == 'friends':
            self._handleFriends(user, uid, chatId, data, bd_data)
        elif key == 'videos':
            self._handleVideos(user, uid, chatId, data, bd_data)
        elif key == 'photos':
            self._handlePhotos(user, uid, chatId, data, bd_data)
        elif key == 'posts':
            self._handlePosts(user, uid, chatId, data, bd_data)

        self.red.set(bd_key, json.dumps(data))

    def _handlePrivate(self, user, uid, chatId, data_new, data_old):
        if data_new['bool'] == data_old['bool']:
            return
        if data_new['bool'] is True:
            self.callback(chatId, "Пользователь " + user +  " (" + uid + ") " + "закрыл аккаунт")
        else:
            self.callback(chatId, "Пользователь " + user +  " (" + uid + ") " + "открыл аккаунт")

    def _handleProfile(self, user, uid, chatId, data_new, data_old):
        if data_new == data_old:
            return
        if (data_new['first_name'] + data_new['last_name'])  != (data_old['first_name'] + data_old['last_name']):
            self.callback(chatId, "Пользователь " + user +  " (" + uid + ") " + 'сменил имя с "' + data_old['first_name'] + ' ' + data_old['last_name'] + '"')
        if data_new['city'] != data_old['city']:
            self.callback(chatId, "Пользователь " + user +  " (" + uid + ") " + ' изменил город с "' + data_old['city'] + '" на "' + data_new['city'] + '"')
        if data_new['status'] != data_old['status']:
            self.callback(chatId, "Пользователь " + user +  " (" + uid + ") " + ' изменил статус с "' + data_old['status'] +  '" на "' + data_new['status'] + '"')

    def _listsDiff(self, list1, list2):
        diff1, diff2 = [], []
        for item in list1:
            if item not in list2:
                diff1.append(item)
        for item in list2:
            if item not in list1:
                diff2.append(item)

        return diff1, diff2

    def _handleSubscriptions(self, user, uid, chatId, data_new, data_old):
        added, deleted = self._listsDiff(data_new, data_old)
        if len(added) > 0:
            send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' добавил новые подписки: '
            for item in added:
                send_str += item + ' '
            self.callback(chatId, send_str)
        if len(deleted) > 0:
            send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' удалил подписки: '
            for item in deleted:
                send_str += item + ' '
            self.callback(chatId, send_str)

    def _handleFriends(self, user, uid, chatId, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if (item['first_name'] + item['last_name'])  == (item2['first_name'] + item2['last_name']):
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' добавил в друзья пользователя ' + item['first_name'] + ' ' + item['last_name'] + ' (' + item['id'] + ')' + ' ((' + item['sex'] + '))')
        for item in data_old:
            found = False
            for item2 in data_new:
                if (item['first_name'] + item['last_name'])  == (item2['first_name'] + item2['last_name']):
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' удалил из друзей пользователя ' + item['first_name'] + ' ' + item['last_name'] + ' (' + item['id'] + ')' + ' ((' + item['sex'] + '))')

    def _handleVideos(self, user, uid, chatId, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if item['title']  == item2['title']:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' добавил видео -  ' + item['title'] + '\nUrl: ' + item['url'])
        for item in data_old:
            found = False
            for item2 in data_new:
                if item['title']  == item2['title']:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' удалил видео -  ' + item['title'] + '\nUrl: ' + item['url'])

    def _handlePhotoComments(self, user, uid, chatId, comments_new, comments_old):
        for item in comments_new:
            found = False
            for item2 in comments_old:
                if item == item2:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'У пользователя ' + user +  " (" + uid + ") " + ' новый комментарий под фотографией: ' + item)
        for item in comments_old:
            found = False
            for item2 in comments_new:
                if item == item2:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'У пользователь ' + user +  " (" + uid + ") " + ' удален комментарий под фотографией: ' + item)

    def _handlePhotosFromAlbum(self, user, uid, chatId, album, photos_new, photos_old):
        for item in photos_new:
            found = False
            for item2 in photos_old:
                if item['id'] == item2['id']:
                    found = True
                    #Сравнение комментариев
                    self._handlePhotoComments(user, uid, chatId, item['comments'], item2['comments'])
                    break
            if found is False:
                send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' добавил в альбом "' + album + '" новое фото'
                if len(item['comments']) > 0:
                    send_str += "\nСо следующими комментариями:"
                    for comment in item['comments']:
                        send_str += '\n' + comment
                self.callback(chatId, send_str, images=[item['photo']])
        for item in photos_old:
            found = False
            for item2 in photos_new:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' удалил из альбома "' + album + '" фото'
                if len(item['comments']) > 0:
                    send_str += "\nСо следующими комментариями:"
                    for comment in item['comments']:
                        send_str += '\n' + comment
                self.callback(chatId, send_str, images=[item['photo']])

    def _handlePhotos(self, user, uid, chatId, data_new, data_old):
        for album in data_new:
            found = False
            for album_old in data_old:
                if album['title'] == album_old['title']:
                    found = True
                    #Сравнение конкретных фотографий
                    self._handlePhotosFromAlbum(user, uid, chatId, album['title'] ,album['items'], album_old['items'])
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' добавил новый альбом "' + album['title'] + '"')
                #Перебор и отправка всех новых фотографий
                for photo in album['items']:
                    send_str = ''
                    if len(photo['comments']) > 0:
                        send_str = 'Комментарии к следующей фотографии:'
                        for comment in photo['comments']:
                            send_str += '\n' + comment
                    self.callback(chatId, send_str, images=[photo['photo']])

        for album in data_old:
            found = False
            for album_new in data_new:
                if album['title'] == album_new['title']:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'Пользователь ' + user +  " (" + uid + ") " + ' удалил альбом "' + album['title'] + '"')
                #Перебор и отправка всех старых фотографий
                for photo in album['items']:
                    send_str = ''
                    if len(photo['comments']) > 0:
                        send_str = 'Комментарии к следующей фотографии:'
                        for comment in photo['comments']:
                            send_str += '\n' + comment
                    self.callback(chatId, send_str, images=[photo['photo']])

    def _handlePostComments(self, user, uid, chatId, comments_new, comments_old):
        for item in comments_new:
            found = False
            for item2 in comments_old:
                if item == item2:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'У пользователя ' + user +  " (" + uid + ") " + ' новый комментарий под постом: ' + item)
        for item in comments_old:
            found = False
            for item2 in comments_new:
                if item == item2:
                    found = True
                    break
            if found is False:
                self.callback(chatId, 'У пользователя ' + user +  " (" + uid + ") " + ' удален комментарий под постом: ' + item)

    def _handlePosts(self, user, uid, chatId, data_new, data_old):
        for item in data_new:
            found = False
            for item2 in data_old:
                if item['id']  == item2['id']:
                    found = True
                    #Сравнение комментов
                    self._handlePostComments(user, uid, chatId, item['comments'], item2['comments'])
                    break
            if found is False:
                send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' добавил новый пост: ' + item['text']
                send_images = []
                if len(item['comments']) > 0:
                    send_str += '\nСо следующими комментариями:'
                    for comment in item['comments']:
                        send_str += '\n' + comment
                for photo in item['attachments']:
                    send_images.append(photo['photo'])
                self.callback(chatId, send_str, images=send_images)
        for item in data_old:
            found = False
            for item2 in data_new:
                if item['id']  == item2['id']:
                    found = True
                    break
            if found is False:
                send_str = 'Пользователь ' + user +  " (" + uid + ") " + ' удалил пост: ' + item['text']
                send_images = []
                if len(item['comments']) > 0:
                    send_str += '\nСо следующими комментариями:'
                    for comment in item['comments']:
                        send_str += '\n' + comment
                for photo in item['attachments']:
                    send_images.append(photo['photo'])
                self.callback(chatId, send_str, images=send_images)

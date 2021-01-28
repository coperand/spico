import json
import redis

class InstaAnalyzer:

    def __init__(self, callback):
        self.callback = callback
        self.red = redis.Redis()

    def removeUser(self, user):
        keys = ['private', 'profile', 'followings', 'posts', 'stories', 'tags', 'highlights']
        for key in keys:
            bd_key = 'insta-' + user + '-' + key
            self.red.delete(bd_key)

    def handleData(self, user, key, data):
        bd_key = 'insta-' + user + '-' + key
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
        elif key == 'posts':
            self._handlePosts(user, data, bd_data)
        elif key == 'stories':
            self._handleStories(user, data, bd_data)
        elif key == 'tags':
            self._handleTags(user, data, bd_data)
        elif key == 'highlights':
            self._handleHighlights(user, data, bd_data)

        self.red.set(bd_key, json.dumps(data))

    def _handlePrivate(self, user, data_new, data_old):
        if data_new['bool'] == data_old['bool']:
            return
        if data_new['bool'] is True:
            self.callback(user, "Пользователь @" + user + " закрыл аккаунт")
        else:
            self.callback(user, "Пользователь @" + user + " открыл аккаунт")

    def _handleProfile(self, user, data_new, data_old):
        if data_new == data_old:
            return
        if data_new['name'] != data_old['name']:
            self.callback(user, "Пользователь @" + user + " сменил имя с " + data_old['name'] + " на " + data_new['name'])
        if data_new['bio'] != data_old['bio']:
            self.callback(user, "Пользователь @" + user + " сменил биографию с " + data_old['bio'] + " на " + data_new['bio'])
        if data_new['avatar_id'] != data_old['avatar_id']:
            self.callback(user, "Пользователь @" + user + " сменил аватар", images=[data_old['avatar'], data_new['avatar']])

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
            send_str = 'Пользователь @' + user + ' подписался на следующие страницы: '
            for item in added:
                send_str += '@' + item + ' '
            self.callback(user, send_str)
        if len(deleted) > 0:
            send_str = 'Пользователь @' + user + ' отписался от следующих страниц: '
            for item in deleted:
                send_str += '@' + item + ' '
            self.callback(user, send_str)

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
                    cdiff1, cdiff2 = self._commentsDiff(item, item2)
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

    def _handlePosts(self, user, data_new, data_old):
        added, deleted, added_comments, deleted_comments = self._postsDiff(data_new, data_old)
        if len(added) > 0:
            for item in added:
                send_str = ''
                send_images = []
                send_videos = []
                if item['type'] == 8:
                    send_str = 'Пользователь @' + user + ' выложил новый пост'
                    for car_data in item['carousel']:
                        if car_data['type'] == 1:
                            send_images.append(car_data['photo'])
                        elif car_data['type'] == 2:
                            send_videos.append(car_data['video'])
                else:
                    if item['type'] == 1:
                        send_images.append(item['photo'])
                    elif item['type'] == 2:
                        send_videos.append(item['video'])

                comments_str = ''
                if len(item['comments']) > 0:
                    comments_str = 'Со следующими комментариями:'
                    for comment in item['comments']:
                        comments_str += '\n@' + comment['user'] + ': ' + comment['text']
                self.callback(user, send_str + (('\n' + comments_str) if comments_str != '' else ''), images=send_images, videos=send_videos)
        if len(deleted) > 0:
            for item in deleted:
                send_str = ''
                send_images = []
                send_videos = []
                if item['type'] == 8:
                    send_str = 'Пользователь @' + user + ' удалил пост'
                    for car_data in item['carousel']:
                        if car_data['type'] == 1:
                            send_images.append(car_data['photo'])
                        elif car_data['type'] == 2:
                            send_videos.append(car_data['video'])
                else:
                    if item['type'] == 1:
                        send_images.append(item['photo'])
                    elif item['type'] == 2:
                        send_videos.append(item['video'])

                comments_str = ''
                if len(item['comments']) > 0:
                    comments_str = 'Со следующими комментариями:'
                    for comment in item['comments']:
                        comments_str += '\n@' + comment['user'] + ': ' + comment['text']
                self.callback(user, send_str + (('\n' + comments_str) if comments_str != '' else ''), images=send_images, videos=send_videos)

        if len(added_comments) > 0:
            for item in added_comments:
                for comment in item['changes']:
                    self.callback(user, 'У пользователя @' + user + ' новый комментарий от @' + comment['user'] + ': ' + comment['text'])
        if len(deleted_comments) > 0:
            for item in deleted_comments:
                for comment in item['changes']:
                    self.callback(user, 'У пользователя @' + user + ' удален комментарий от @' + comment['user'] + ': ' + comment['text'] + ' under the post: ' + item['item']['id'])

    def _handleStories(self, user, data_new, data_old):
        if data_new is None and data_old is not None:
            return
        elif data_new is None:
            return
        elif data_new is not None and data_old is None:
            for item in data_new:
                if item['type'] == 1:
                    self.callback(user, 'Пользователь @' + user + ' выложил новую историю', images=[item['photo']])
                elif item['type'] == 2:
                    self.callback(user, 'Пользователь @' + user + ' выложил новую историю', videos=[item['video']])
        else:
            for item in data_new:
                found = False
                for item2 in data_old:
                    if item['id'] == item2['id']:
                        found = True
                        break
                if found is False:
                    if item['type'] == 1:
                        self.callback(user, 'Пользователь @' + user + ' выложил новую историю', images=[item['photo']])
                    elif item['type'] == 2:
                        self.callback(user, 'Пользователь @' + user + ' выложил новую историю', videos=[item['video']])

            for item in data_old:
                found = False
                for item2 in data_new:
                    if item['id'] == item2['id']:
                        found = True
                        break

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
                send_str = ''
                send_images = []
                send_videos = []
                if item['type'] == 8:
                    send_str = 'Пользователя @' + user + ' отметили в посте'
                    for car_data in item['carousel']:
                        if car_data['type'] == 1:
                            send_images.append(car_data['photo'])
                        elif car_data['type'] == 2:
                            send_videos.append(car_data['video'])
                else:
                    if item['type'] == 1:
                        send_images.append(item['photo'])
                    elif item['type'] == 2:
                        send_videos.append(item['video'])
                self.callback(user, send_str, images=send_images, videos=send_videos)

        if len(deleted) > 0:
            for item in deleted:
                send_str = ''
                send_images = []
                send_videos = []
                if item['type'] == 8:
                    send_str = 'Пользователя @' + user + ' убрали из отмеченных в посте'
                    for car_data in item['carousel']:
                        if car_data['type'] == 1:
                            send_images.append(car_data['photo'])
                        elif car_data['type'] == 2:
                            send_videos.append(car_data['video'])
                else:
                    if item['type'] == 1:
                        send_images.append(item['photo'])
                    elif item['type'] == 2:
                        send_videos.append(item['video'])
                self.callback(user, send_str, images=send_images, videos=send_videos)

    def _handleReelMedia(self, user, highlight, stories_new, stories_old):
        for item in stories_new:
            found = False
            for item2 in stories_old:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                if item['type'] == 1:
                    self.callback(user, 'Пользователь @' + user + ' добавил историю в актуальное: ' + highlight, images=[item['photo']])
                elif item['type'] == 2:
                    self.callback(user, 'Пользователь @' + user + ' добавил историю в актуальное: ' + highlight, videos=[item['video']])
        for item in stories_old:
            found = False
            for item2 in stories_new:
                if item['id'] == item2['id']:
                    found = True
                    break
            if found is False:
                if item['type'] == 1:
                    self.callback(user, 'Пользователь @' + user + ' удалил историю из актуального: ' + highlight, images=[item['photo']])
                elif item['type'] == 2:
                    self.callback(user, 'Пользователь @' + user + ' удалил историю из актуального: ' + highlight, videos=[item['video']])

    def _handleHighlights(self, user, data_new, data_old):
        for highlight in data_new:
            found = False
            for highlight_old in data_old:
                if highlight['title'] == highlight_old['title']:
                    found = True
                    #Сравнение конкретных историй
                    self._handleReelMedia(user, highlight['title'] ,highlight['stories'], highlight_old['stories'])
                    break
            if found is False:
                #Перебор и отправка всех новых историй
                send_str = 'Пользователь @' + user + ' добавил новое актуальное: ' + highlight['title']
                send_images = []
                send_videos = []
                for story in highlight['stories']:
                    if story['type'] == 1:
                        send_images.append(story['photo'])
                    elif story['type'] == 2:
                        send_videos.append(story['video'])
                self.callback(user, send_str, images=send_images, videos=send_videos)

        for highlight in data_old:
            found = False
            for highlight_new in data_new:
                if highlight['title'] == highlight_new['title']:
                    found = True
                    break
            if found is False:
                #Перебор и отправка всех старых историй
                send_str = 'Пользователь @' + user + ' удалил актуальное: ' + highlight['title']
                send_images = []
                send_videos = []
                for story in highlight['stories']:
                    if story['type'] == 1:
                        send_images.append(story['photo'])
                    elif story['type'] == 2:
                        send_videos.append(story['video'])
                self.callback(user, send_str, images=send_images, videos=send_videos)

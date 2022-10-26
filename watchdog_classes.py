from pathlib import Path
import json

import requests


class YaDisk:
    def __init__(self, token):
        '''
        Uploads a video file to Yandex Disk and publishes it and then returns url of the shared video.
        '''
        self.headers = {'Authorization': f'OAuth {token}'}
        self.last_uploaded = None

    def upload(self, file_to_upload):
        '''
            Uploads provided file to Yandex Disk and sets file's path on disk to self.last_uploaded
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        res = requests.get(url, headers=self.headers,
                           params={'path': file_to_upload})
        # print(res.text, res.status_code)
        if res.status_code == 200:
            upload_href = res.json()['href']
            upl = requests.put(upload_href, data=open(
                f'{path}{file_to_upload}', 'rb'))
            # print(upl)
            if upl.status_code == 201:
                self.last_uploaded = file_to_upload
                return True
        # log error to file
        # return res
        return False

    def publish(self):
        '''
            Publishes the last_uploaded file, gets its link and returns the link
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources/publish'
        res = requests.put(
            url, params={'path': self.last_uploaded}, headers=self.headers)
        if res.status_code == 200:
            url = res.json()['href']
            res = requests.get(url, headers=self.headers)
            # print(res.text)
            downloader = res.json()['file']
            public_url = res.json()['public_url']
            return (public_url, downloader)
        # log error to file
        return None

    def delete(self, yd_path_to_delete):
        '''
        Gets a list of filenames to delete on Yandex Disk. Returns list with names of deleted files.
        '''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        deleted_files = []
        for file in yd_path_to_delete:
            # r = requests.delete(url, headers=self.headers, data={'path':file+'.mp4'})
            # f = requests.utils.quote('disk%3A%2F'+file+'.mp4')
            f = 'disk%3A%2F'+file+'.mp4'
            url2 = f'{url}?path={f}&permanently=true'
            # print(f, url2)
            r = requests.delete(url2, headers=self.headers)
            # print(r.status_code,r.text)
            if r.status_code == 204:
                deleted_files.append(file)
        return deleted_files


class TelegramMessageSender:
    def __init__(self, token, chat_id):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{self.token}/'
        self.chat_id = chat_id

    def send_text(self, text_to_send, disable_notification=False):
        r = requests.post(self.base_url + 'sendMessage', data={'chat_id': self.chat_id,
                                                               'text': text_to_send, 'disable_notification': disable_notification})
        return r

    def send_video(self, video, caption=None):
        '''If path is passed as parameter, uploads a new video using multipart/form-data otherwise will use str as file_id or url'''
        videopath = Path(video)
        if not videopath.is_file():
            r = requests.post(self.base_url + 'sendVideo', data={'chat_id': self.chat_id,
                                                                 'video': video, 'caption': caption})
        else:
            r = requests.post(self.base_url + 'sendVideo',
                              data={'chat_id': self.chat_id}, files={'video': videopath.read_bytes()})
        return r

    def send_photo(self, photo):
        r = requests.post(self.base_url + 'sendPhoto',
                          data={'chat_id': self.chat_id, 'photo': photo})
        return r

    def send_animation(self, gif=None):
        r = requests.post(self.base_url + 'sendAnimation',
                          data={'chat_id': self.chat_id, 'animation': gif})
        return r

    def place_video(self, mediafile=None, message_id=None):
        if type(message_id) is not int and mediafile is None:
            raise TypeError(
                '"message_id" should be a number. "mediafile" can\'t be None')
        media = {'type': 'video', 'media': 'attach://media'}
        r = requests.post(self.base_url + 'editMessageMedia',
                          data={'message_id': message_id, 'chat_id': self.chat_id, 'media': json.dumps(media)}, files={'media': open(mediafile, 'rb')})
        return r

    def edit_text_message(self, text=None, message_id=None):
        if type(text) is not str and type(message_id) is not int:
            raise TypeError(
                'Message Id should be a number. Text can\'t be None')
        r = requests.post(self.base_url + 'editMessageText',
                          data={'chat_id': self.chat_id, 'text': text, 'message_id': message_id})
        return r

class YaDisk:
    def __init__(self, token):
        '''
        Uploads a video file to Yandex Cloud and publishes it and then returns url of the shared video.
        '''
        self.headers = {'Authorization':f'OAuth {token}'}
        self.last_uploaded = None

    def upload(self, file_to_upload):
            '''
                Uploads provided file to YandexCloud and sets file's path on cloud to self.last_uploaded
            '''

            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            res = requests.get(url, headers=self.headers, params={'path':file_to_upload})
            #print(res.text, res.status_code)
            if res.status_code == 200:
                upload_href = res.json()['href']
                upl = requests.put(upload_href, data=open(f'{path}{file_to_upload}', 'rb'))
                #print(upl)
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
            res = requests.put(url, params={'path': self.last_uploaded}, headers=self.headers)
            if res.status_code == 200:
                url = res.json()['href']
                res = requests.get(url, headers=self.headers)
                #print(res.text)
                downloader = res.json()['file']
                public_url = res.json()['public_url']
                return (public_url, downloader)
            # log error to file
            return None


    def delete(self, yd_path_to_delete):
        '''
        Gets a list of filenames to delete on yadisk. Returns list with names of deleted files.
        '''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        deleted_files = []
        for file in yd_path_to_delete:
            #r = requests.delete(url, headers=self.headers, data={'path':file+'.mp4'})
            #f = requests.utils.quote('disk%3A%2F'+file+'.mp4')
            f = 'disk%3A%2F'+file+'.mp4'
            url2 = f'{url}?path={f}&permanently=true'
            #print(f, url2)
            r = requests.delete(url2, headers=self.headers)
            #print(r.status_code,r.text)
            if r.status_code == 204:
                deleted_files.append(file)
        return deleted_files
import os
from time import sleep
from nanome.util import Logs

import requests
import shutil

class MatryxCortex():
    def __init__(self, url):
        self._url = url
        self._artifacts = self.get_artifacts()

        self._ipfs_url = 'https://ipfs.infura.io:5001/api/v0/'

    def ipfs_list_dir(self, ipfs_hash):
        url = self._ipfs_url + 'object/get?arg=' + ipfs_hash
        json = requests.get(url).json()
        return json['Links']

    def ipfs_download_file(self, ipfs_hash):
        path = 'temp/ipfs/' + ipfs_hash

        if not os.path.isfile(path):
            url = self._ipfs_url + 'cat?arg=' + ipfs_hash
            response = requests.get(url, stream=True)

            with open(path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)

        return path

    def ipfs_get_file_contents(self, ipfs_hash):
        path = self.ipfs_download_file(ipfs_hash)

        with open(path, 'r') as file:
            return file.read()

    def upload_json(self, json):
        response = requests.post(self._url + '/upload/json', json=json)
        return response.json()['data']['hash']

    def upload_files(self, paths):
        files = []
        for path in paths:
            files.append(("files", open(path, 'rb')))

        response = requests.post(self._url + '/upload/files', files=files)
        ipfs_hash = response.json()['data']['hash']
        Logs.debug('ipfs hash', ipfs_hash)
        return ipfs_hash

    def get_json(self, path, params=None):
        json = requests.get(self._url + path, params).json()
        return json['data']

    def get_artifacts(self):
        return self.get_json('/artifacts')

    def get_tournaments(self, params=None):
        return self.get_json('/tournaments', params)['tournaments']

    def get_tournament(self, address):
        return self.get_json('/tournaments/' + address)['tournament']

    def get_round(self, address, index):
        return self.get_json('/tournaments/%s/round/%d' % (address, index))['round']

    def get_submission(self, hash):
        return self.get_json('/submissions/%s' % hash)['submission']

    def get_commits(self, owner, params=None):
        return self.get_json('/commits/owner/' + owner, params)['commits']

    def get_commit(self, hash):
        return self.get_json('/commits/' + hash)['commit']

import os
from nanome.util import Logs

import requests
import shutil
from web3 import Web3, HTTPProvider

class MatryxCortex():
    def __init__(self, url):
        self._url = url
        self._artifacts = self.get_artifacts()

        self._ipfs_url = 'https://ipfs.infura.io:5001/api/v0/'

        self._provider = HTTPProvider('https://ropsten.infura.io/v3/2373e82fc83341ff82b66c5a87edd5f5')
        self._w3 = Web3(self._provider)

        self._token = self._w3.eth.contract(
            address=self._artifacts['token']['address'],
            abi=self._artifacts['token']['abi']
        )

    def ipfs_list_dir(self, ipfs_hash):
        url = self._ipfs_url + 'object/get?arg=' + ipfs_hash
        json = requests.get(url).json()
        return json['Links']

    def ipfs_download_file(self, ipfs_hash):
        path = 'ipfs_cache/' + ipfs_hash

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

    def get_commits(self, owner):
        return self.get_json('/commits/owner/' + owner)['commits']

    def get_mtx(self, owner):
        wei = self._token.functions.balanceOf(owner).call()
        return Web3.fromWei(wei, 'ether')

    def get_eth(self, owner):
        wei = self._w3.eth.getBalance(owner)
        return Web3.fromWei(wei, 'ether')

from nanome.util import Logs

import requests
from web3 import Web3, HTTPProvider

class MatryxCortex():
    def __init__(self, url):
        self._url = url
        self._artifacts = self.get_artifacts()

        self._provider = HTTPProvider('https://ropsten.infura.io/v3/2373e82fc83341ff82b66c5a87edd5f5')
        self._w3 = Web3(self._provider)

        self._token = self._w3.eth.contract(
            address=self._artifacts['token']['address'],
            abi=self._artifacts['token']['abi']
        )

    def get_json(self, path, params=None):
        Logs.debug('fetching ' + path)
        json = requests.get(self._url + path, params).json()
        Logs.debug('got ' + path)
        return json['data']

    def get_artifacts(self):
        return self.get_json('/artifacts')

    def get_tournaments(self, params=None):
        return self.get_json('/tournaments', params)['tournaments']

    def get_tournament(self, address):
        return self.get_json('/tournaments/' + address)['tournament']

    def get_round(self, address, index):
        return self.get_json('/tournaments/%s/round/%d' % (address, index))['round']

    def get_commits(self, owner):
        return self.get_json('/commits/owner/' + owner)['commits']

    def get_mtx(self, owner):
        wei = self._token.functions.balanceOf(owner).call()
        return Web3.fromWei(wei, 'ether')

    def get_eth(self, owner):
        wei = self._w3.eth.getBalance(owner)
        return Web3.fromWei(wei, 'ether')

import requests


class MatryxCortex():
    def __init__(self, url):
        self._url = url
        self._artifacts = self.get_artifacts()

    def get_json(self, path, params=None):
        json = requests.get(self._url + path, params).json()
        return json['data']

    def get_artifacts(self):
        return self.get_json('/artifacts')

    def get_tournaments(self, params=None):
        return self.get_json('/tournaments', params)['tournaments']

    def get_commits(self, owner):
        return self.get_json('/commits/owner/' + owner)['commits']

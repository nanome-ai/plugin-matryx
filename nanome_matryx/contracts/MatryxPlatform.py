from datetime import datetime
from nanome.util import Logs

class MatryxPlatform():
    def __init__(self, plugin):
        self._plugin = plugin
        self._contract = plugin._web3.get_contract('platform')

        self.address = self._contract.address

    def create_submission(self, ipfs_hash, commit_hash):
        fn = self._plugin._web3._platform.create_submission(ipfs_hash, commit_hash)
        return self._plugin._web3.send_tx(fn)

    def create_tournament(self, content, bounty, entryfee, start_datetime, end_datetime, review_length=60*60*24*7):
        epoch = datetime.utcfromtimestamp(0)
        diff_seconds = lambda start, end: int((end - start).total_seconds())

        start = diff_seconds(epoch, start_datetime)
        duration = diff_seconds(start_datetime, end_datetime)

        t_details = (content, bounty, entryfee)
        r_details = (start, duration, review_length, bounty)

        fn = self._contract.functions.createTournament(t_details, r_details)
        return self._plugin._web3.send_tx(fn)

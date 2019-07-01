from nanome.util import Logs

class MatryxTournament():
    def __init__(self, plugin, address):
        self._plugin = plugin
        self._contract = plugin._web3.get_contract('tournament', address)

        self.address = address

    def isEntrant(self, user):
        return self._contract.functions.isEntrant(user).call()

    def addToBounty(self, amount):
        return self._contract.functions.addToBounty(amount).call()

    def enter(self):
        fn = self._contract.functions.enter()
        return self._plugin._web3.send_tx(fn)

    def exit(self):
        fn = self._contract.functions.exit()
        return self._plugin._web3.send_tx(fn)

    def create_submission(self, info_hash, commit_hash):
        fn = self._contract.functions.createSubmission(info_hash, commit_hash)
        return self._plugin._web3.send_tx(fn)

    def select_winners(self, zipped_winners, action, round_info=None):
        d, w = zip(*zipped_winners)
        distribution, winners = list(d), list(w)

        winners_struct = (winners, distribution, action)

        if not round_info:
            round_info = (0, 0, 0, 0)

        fn = self._contract.functions.selectWinners(winners_struct, round_info)
        return self._plugin._web3.send_tx(fn)
class MatryxTournament():
    def __init__(self, plugin, address):
        self._plugin = plugin
        self._contract = plugin._web3.get_contract('tournament', address)

        self.address = address

    def isEntrant(self, user):
        return self._contract.functions.isEntrant(user).call()

    def enter(self):
        fn = self._contract.functions.enter()
        return self._plugin._web3.send_tx(fn)

    def exit(self):
        fn = self._contract.functions.exit()
        return self._plugin._web3.send_tx(fn)

    def create_submission(self, info_hash, commit_hash):
        fn = self._contract.functions.createSubmission(info_hash, commit_hash)
        return self._plugin._web3.send_tx(fn)
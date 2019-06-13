class MatryxCommit():
    def __init__(self, plugin):
        self._plugin = plugin
        self._contract = plugin._web3.get_contract('commit')

    def claimCommit(self, commitHash):
        fn = self._contract.functions.claimCommit(commitHash)
        return self._plugin._web3.send_tx(fn)

    def createCommit(self, parentHash, isFork, salt, content, value):
        value = self._plugin._web3.to_wei(value)
        fn = self._contract.functions.createCommit(parentHash, isFork, salt, content, value)
        return self._plugin._web3.send_tx(fn)

    def createSubmission(self, tAddress, content, parentHash, isFork, salt, commitContent, value):
        value = self._plugin._web3.to_wei(value)
        fn = self._contract.functions.createSubmission(tAddress, content, parentHash, isFork, salt, commitContent, value)
        return self._plugin._web3.send_tx(fn)

    def getAvailableRewardForUser(self, commitHash):
        fn = self._contract.functions.getAvailableRewardForUser(commitHash)
        return self._plugin._web3.send_tx(fn)

    def withdrawAvailableReward(self, commitHash):
        fn = self._contract.functions.withdrawAvailableReward(commitHash)
        return self._plugin._web3.send_tx(fn)
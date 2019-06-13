class MatryxToken():
    def __init__(self, plugin):
        self._plugin = plugin
        self._contract = plugin._web3.get_contract('token')

        self.address = self._contract.address

    def balanceOf(self, address):
        amount = self._contract.functions.balanceOf(address).call()
        return self._plugin._web3.from_wei(amount)

    def allowance(self, user, spender):
        amount = self._contract.functions.allowance(user, spender).call()
        return self._plugin._web3.from_wei(amount)

    def approve(self, spender, amount):
        amount = self._plugin._web3.to_wei(amount)
        fn = self._contract.functions.approve(spender, amount)
        return self._plugin._web3.send_tx(fn)

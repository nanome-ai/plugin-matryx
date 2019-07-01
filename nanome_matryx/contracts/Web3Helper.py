from nanome.util import Logs

from time import sleep
from web3 import Web3, HTTPProvider, exceptions

from contracts.MatryxToken import MatryxToken
from contracts.MatryxPlatform import MatryxPlatform
from contracts.MatryxCommit import MatryxCommit

class Web3Helper():
    def __init__(self, plugin):
        self._plugin = plugin

        self._provider = HTTPProvider('https://ropsten.infura.io/v3/2373e82fc83341ff82b66c5a87edd5f5')
        self._web3 = Web3(self._provider)

    def setup(self):
        self._token = MatryxToken(self._plugin)
        self._platform = MatryxPlatform(self._plugin)
        self._commit = MatryxCommit(self._plugin)

    def account_from_key(self, private_key):
        return self._web3.eth.account.privateKeyToAccount(private_key)

    def solidity_sha3(self, types, values):
        for i, value in enumerate(values):
            if types[i] == 'address':
                values[i] = self._web3.toChecksumAddress(value)
        return self._web3.soliditySha3(types, values).hex()

    def from_wei(self, amount, unit='ether'):
        return self._web3.fromWei(amount, unit)

    def to_wei(self, amount, unit='ether'):
        return self._web3.toWei(amount, unit)

    def get_contract(self, contract_type, address=None):
        if address is None:
            address = self._plugin._cortex._artifacts[contract_type]['address']

        address = self._web3.toChecksumAddress(address)
        abi = self._plugin._cortex._artifacts[contract_type]['abi']
        return self._web3.eth.contract(abi=abi, address=address)

    def get_eth(self, address):
        wei = self._web3.eth.getBalance(address)
        return self.from_wei(wei)

    def get_mtx(self, address):
        return self._token.balanceOf(address)

    def get_allowance(self, address):
        return self._token.allowance(address, self._platform.address)

    def estimate_gas(self, fn):
        caller = self._plugin._account.address
        tx = fn.buildTransaction({'from': caller})
        return self._web3.eth.estimateGas(tx)

    def create_tx(self, fn):
        caller = self._plugin._account.address
        gas = self.estimate_gas(fn)
        nonce = self._web3.eth.getTransactionCount(caller)

        return fn.buildTransaction({
            'from': caller,
            'gas': gas,
            'gasPrice': self.to_wei('4', 'gwei'),
            'nonce': nonce
        })

    def send_tx(self, fn):
        try:
            account = self._plugin._account
            signed_tx = account.signTransaction(self.create_tx(fn))
            receipt = self._web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            tx_hash = receipt.hex()
            Logs.debug("%s tx %s" % (fn.fn_name, tx_hash))
            return tx_hash
        except ValueError as err:
            Logs.debug('%s tx revert, revert!' % fn.fn_name)
            raise err

    def wait_for_tx(self, tx_hash, poll_interval=1):
        if not tx_hash:
            return None

        tx_receipt = None
        mined_block = None

        while True:
            sleep(poll_interval)
            try:
                tx_receipt = self._web3.eth.getTransactionReceipt(tx_hash)
                if tx_receipt:
                    mined_block = tx_receipt.blockNumber
                    Logs.debug('tx %s mined' % tx_hash)
                    break
            except exceptions.TransactionNotFound:
                sleep(5)

        while self._web3.eth.blockNumber <= mined_block:
            sleep(5)

        return tx_receipt
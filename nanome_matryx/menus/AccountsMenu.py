import os
import json
from functools import partial

import nanome
import utils
from nanome.util import Logs

from web3 import Web3, HTTPProvider
import blockies

class AccountsMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/accounts.json')
        menu.register_closed_callback(on_close)

        self._accounts_list = menu.root.find_node('Accounts List').get_content()
        self._prefab_account_item = menu.root.find_node('Account Item Prefab')

        self._info = menu.root.find_node('Info')
        self._info.get_content().text_value = "Account private keys are loaded from \n/path/to/file\n If you don't see any accounts here, please add your key to \n/path/to/file"

        self._wallet_json = ''

        self._menu = menu

    def show_menu(self, button):
        self._plugin.open_menu(self._menu)

        if len(self._accounts_list.items) == 0:
            self.populate_accounts()

    def load_private_keys(self):
        Logs.debug(self._wallet_json)
        try:
            wallet = json.loads(self._wallet_json)
            Logs.debug('wallet: ' + str(wallet))
            if 'keys' in wallet:
                return wallet['keys']
            else:
                Logs.debug("here")
                self._plugin._modal.show_error('Wallet uninitialized. Visit blog.matryx.ai for more info')
                return ''
        except:
            self._plugin._modal.show_error('Wallet uninitialized. Visit blog.matryx.ai for more info')
            return ''

    def populate_accounts(self):
        keys = self.load_private_keys()
        self._accounts_list.items = []

        for key in keys:
            account = self._plugin._web3.account_from_key(key)

            address = account.address.lower()
            short_address = utils.short_address(address)

            filepath = os.path.join(os.path.dirname(__file__), '../temp/blockies/' + address + '.png')
            with open(filepath, 'wb') as png:
                blockie = blockies.create(address, scale=64)
                png.write(blockie)
                png.close()

            account.blockie = filepath
            account.short_address = short_address

            account_item = self._prefab_account_item.clone()
            account_item.enabled = True

            button = account_item.get_content()
            button.register_pressed_callback(partial(self._plugin.select_account, account))

            account_item.find_node('Blockie').add_new_image(filepath)
            account_item.find_node('Address').get_content().text_value = short_address

            self._accounts_list.items.append(account_item)

        self._plugin.refresh_menu()
import os
from functools import partial

import nanome
import utils
from nanome.util import Logs

from web3 import Web3, HTTPProvider
from eth_account import Account
import blockies

class AccountsMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json("menus/accounts.json")
        menu.register_closed_callback(on_close)

        self._accounts_list = menu.root.find_node('Accounts List').get_content()
        self._prefab_account_item = menu.root.find_node('Account Item Prefab')

        self._menu = menu

    def show_menu(self, button):
        self._plugin.open_menu(self._menu)

        if len(self._accounts_list.items) == 0:
            self.populate_accounts()

    def load_private_keys(self):
        return [
            # dev mnemonic accounts from MatryxPlatform
            '0x2c22c05cb1417cbd17c57c1bd0f50142d8d7884984e07b2d272c24c6e120a9ea', # daa
            '0x67a8bc7c12985775e9ab2b1bc217a9c4eff822f93a6f388021e30431d26cb3d3', # ecc
            '0x42811f2725f3c7a7608535fba191ea9a167909883f1e76e038c3168446fbc1bc'  # 8ad
        ]

    def populate_accounts(self):
        keys = self.load_private_keys()
        self._accounts_list.items = []

        for key in keys:
            account = Account.from_key(key)

            address = account.address.lower()
            short_address = utils.short_address(address)

            filepath = os.path.join(os.path.dirname(__file__), 'blockies/' + address + '.png')
            with open(filepath, 'wb') as png:
                blockie = blockies.create(address, scale=64)
                png.write(blockie)
                png.close()

            account.blockie = filepath
            account.short_address = short_address

            account_item = self._prefab_account_item.clone()
            account_item.enabled = True

            button = account_item.get_content()
            button.register_pressed_callback(partial(self.select_account, account))

            account_item.find_node('Blockie').add_new_image(filepath)
            account_item.find_node('Address').get_content().text_value = short_address

            self._accounts_list.items.append(account_item)

        self._plugin.refresh_menu()

    def select_account(self, account, button=None):
        self._plugin.update_account(account)
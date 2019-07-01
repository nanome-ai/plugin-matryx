import requests
from functools import partial

import nanome
import utils
from nanome.util import Logs

class CreationMenu:
    def __init__(self, _plugin, on_close):
        self._plugin = _plugin

        menu_creation = nanome.ui.Menu.io.from_json('menus/json/creation.json')
        menu_creation.register_closed_callback(on_close)
        self._menu_creation = menu_creation

        self._button_parent = menu_creation.root.find_node('Parent Button')
        self._button_parent.enabled = False
        self._commit_name = menu_creation.root.find_node('Commit Name').get_content()
        self._commit_author = menu_creation.root.find_node('Commit Author').get_content()
        self._commit_date = menu_creation.root.find_node('Commit Date').get_content()
        self._button_withdraw = menu_creation.root.find_node('Withdraw Button')
        self._files_list = menu_creation.root.find_node('Files List').get_content()
        self._child_list = menu_creation.root.find_node('Child List').get_content()
        self._prefab_list_item = menu_creation.root.find_node('List Item Prefab')
        self._bottom = menu_creation.root.find_node('Bottom')

    def load_commit(self, commit_hash, button):
        commit = self._plugin._cortex.get_commit(commit_hash)
        self.populate_header(commit)
        self.load_files(commit)
        self.load_children(commit)
        self.setup_withdraw_button(commit)

        self._plugin.open_menu(self._menu_creation)

    def populate_header(self, commit):
        self._commit_name.text_value = commit['hash'][2:10]
        self._commit_author.text_value = 'by ' + utils.short_address(commit['owner'])
        self._commit_date.text_value = utils.timestamp_to_date(commit['timestamp'])

    def load_files(self, commit):
        files = self._plugin._cortex.ipfs_list_dir(commit['ipfsContent'])

        # change format depending on numbers
        num_columns = 1 if len(files) < 6 else 2
        self._files_list.display_columns = num_columns
        self._files_list.total_columns = num_columns

        self._files_list.items = []
        for file in files:
            clone = self._prefab_list_item.clone()
            btn = clone.get_content()
            btn.register_pressed_callback(partial(self._plugin._menu_files.view_file, file))
            clone.find_node('Item Parent').enabled = False
            clone.find_node('Item Name').get_content().text_value = file['Name']
            clone.find_node('Item Size').get_content().text_value = utils.file_size(file['Size'])
            self._files_list.items.append(clone)

    def load_children(self, commit):
        self._bottom.enabled = len(commit['children']) != 0

        self._child_list.items = []
        for child in commit['children']:
            clone = self._prefab_list_item.clone()
            btn = clone.get_content()
            btn.register_pressed_callback(partial(self.load_commit, child))

    def setup_withdraw_button(self, commit):
        # get balance on commit
        user = self._plugin._account.address
        mtx = self._plugin._web3._commit.getAvailableRewardForUser(commit['hash'], user)

        self._button_withdraw.enabled = mtx > 0
        self._button_withdraw.get_content().set_all_text("withdraw %s MTX" % utils.truncate(mtx))

        def cb(b):
            self._button_withdraw.enabled = False
            self._plugin._modal.show_message('Withdrawing your MTX...')

            tx_hash = self._plugin._web3._commit.withdrawAvailableReward(commit['hash'])
            self._plugin._web3.wait_for_tx(tx_hash)

            self._plugin.update_account()
            self._plugin._modal.show_message('MTX sucessfully withdrawn')

        self._button_withdraw.get_content().register_pressed_callback(cb)
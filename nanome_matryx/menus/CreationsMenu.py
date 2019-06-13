from functools import partial

import nanome
import utils
from nanome.util import Logs

class CreationsMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/my_creations.json')
        menu.register_closed_callback(on_close)
        self._menu = menu

        self._creation_menu = nanome.ui.Menu.io.from_json('menus/json/creation.json')
        self._creation_menu.register_closed_callback(on_close)

        self._list = menu.root.find_node('List').get_content()

        self._prefab_commit_item = menu.root.find_node('Prefab Commit Item')

    def open_my_creations(self, button):
        commits = self._plugin._cortex.get_commits(self._plugin._account.address)
        self._list.items = []

        for commit in commits:
            clone = self._prefab_commit_item.clone()
            clone.find_node('Label').get_content().text_value = 'Commit ' + commit['hash'][2:10]

            btn = clone.get_content()
            btn.register_pressed_callback(partial(self.open_creation_menu, commit['hash']))

            btn = clone.find_node('Submit').get_content()
            callback = partial(self._plugin._menu_tournament.open_submit_menu, commit['hash'])
            btn.register_pressed_callback(callback)

            self._list.items.append(clone)

        self._plugin.open_menu(self._menu)

    def open_creation_menu(self, commit_hash, button):
        commit = self._plugin._cortex.get_commit(commit_hash)

        address = self._creation_menu.root.find_node('Address').get_content()
        address.text_value = 'Commit ' + commit['hash'][2:10]

        author = self._creation_menu.root.find_node('Author').get_content()
        author.text_value = 'by ' + utils.short_address(commit['owner'])

        submit_time = self._creation_menu.root.find_node('Time').get_content()
        submit_time.text_value = utils.timestamp_to_date(commit['timestamp'])

        child_list = self._creation_menu.root.find_node('Children List').get_content()
        child_list.items = []

        btn_view_files = self._creation_menu.root.find_node('View Files').get_content()
        callback = partial(self._plugin._menu_files.load_files, commit['ipfsContent'])
        btn_view_files.register_pressed_callback(callback)

        commit['children'] = [commit] * 10
        for child in commit['children']:
            item = nanome.ui.LayoutNode()

            btn = item.add_new_button()
            btn.set_all_text(child['hash'][2:10])
            btn.register_pressed_callback(partial(self.open_creation_menu, child['hash']))

            child_list.items.append(item)

        self._plugin.open_menu(self._creation_menu)

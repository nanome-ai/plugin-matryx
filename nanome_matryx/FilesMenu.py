import requests
import nanome
import utils
from nanome.util import Logs

class FilesMenu:
    def __init__(self, _plugin, on_close):
        self._plugin = _plugin

        menu = nanome.ui.Menu.io.from_json('_files_menu.json')
        menu.register_closed_callback(on_close)

        self._prefab_file_item = nanome.ui.LayoutNode()
        child = self._prefab_file_item.create_child_node()
        child.forward_dist = 0.002
        child.add_new_button()

        self._files_list = menu.root.find_node('List').get_content()

        self._menu = menu

    def load_files(self, button):
        ipfs_hash = button.ipfs_hash

        files = requests.get('https://ipfs.infura.io:5001/api/v0/object/get?arg=' + ipfs_hash).json()
        files = files['Links']

        self._files_list.items = []

        for file in files:
            clone = self._prefab_file_item.clone()
            btn = clone.get_children()[0].get_content()
            btn.set_all_text(file['Name'])
            # btn.register_pressed_callback()
            self._files_list.items.append(clone)

        self._plugin.open_menu(self._menu)
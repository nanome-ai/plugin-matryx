import requests
from functools import partial
from pdf2image import convert_from_path

import nanome
import utils
from nanome.util import Logs, Vector3

class FilesMenu:
    def __init__(self, _plugin, on_close):
        self._plugin = _plugin

        menu_files = nanome.ui.Menu.io.from_json('menus/json/files.json')
        menu_files.register_closed_callback(on_close)
        self._menu = menu_files

        self._prefab_file_item = menu_files.root.find_node('File Item Prefab')
        self._files_list = menu_files.root.find_node('List').get_content()

        self._menu_view_file = nanome.ui.Menu.io.from_json('menus/json/view_file.json')
        self._menu_view_file.register_closed_callback(on_close)

        self._file_view = self._menu_view_file.root.find_node('File View')
        self._ln_list = self._menu_view_file.root.find_node('List')
        self._ln_import = self._menu_view_file.root.find_node('Import')

        self._prefab_list_item  = self._menu_view_file.root.find_node('List Item Prefab')

    def load_files(self, ipfs_hash, button):
        files = self._plugin._cortex.ipfs_list_dir(ipfs_hash)

        self._files_list.items = []

        for file in files:
            clone = self._prefab_file_item.clone()

            btn = clone.get_content()
            btn.register_pressed_callback(partial(self.view_file, file))

            clone.find_node('Name').get_content().text_value = file['Name']
            clone.find_node('Size').get_content().text_value = utils.file_size(file['Size'])
            self._files_list.items.append(clone)

        self._plugin.open_menu(self._menu)

    def view_file(self, file, button):
        self._ln_import.enabled = False
        self._ln_list.get_content().items = []
        file_parts = file['Name'].split('.')
        file_name = '.'.join(file_parts[:-1])
        ext = file_parts[-1]  # png, json, etc.

        supported_files = ['jpg', 'jpeg', 'png', 'txt', 'rtf']
        if ext in supported_files:
            path = self._plugin._cortex.ipfs_download_file(file['Hash'])

        if ext in ['jpg', 'jpeg', 'png']:
            self._file_view.add_new_image(path)
        elif ext in ['txt', 'rtf']:
            self._ln_list.enabled = True
            item = self._prefab_list_item.clone()
            text = self._plugin._cortex.ipfs_get_file_contents(file['Hash'])
            item.find_node('Content').get_content().text_value = text
            self._ln_list.get_content().items.append(item)
        elif ext in ['cif', 'sdf', 'pdb']:
            self._ln_list.enabled = True
            item = self._prefab_list_item.clone()
            text = self._plugin._cortex.ipfs_get_file_contents(file['Hash'])
            item.find_node('Content').get_content().text_value = text
            self._ln_list.get_content().items.append(item)
            self._ln_import.enabled = True
            self._ln_import.get_content().register_pressed_callback(partial(self.import_file, text, file_name, ext))

        self._plugin.open_menu(self._menu_view_file)

    def import_file(self, file_text, file_name, ext, button):
        lines = file_text.split('\n')
        suffix = ext if ext != 'cif' else 'mmcif'
        complex = getattr(nanome.api.structure.Complex.io, 'from_' + suffix) (lines=lines)
        complex.name = file_name
        complex.position = Vector3()
        self._plugin.add_bonds([complex], self._plugin.add_to_workspace)
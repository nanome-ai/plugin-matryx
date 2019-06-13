import nanome

class Modal:
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        self._menu = nanome.ui.Menu.io.from_json('menus/json/modal.json')
        self._menu.register_closed_callback(on_close)

        self._label = self._menu.root.find_node('Label').get_content()

    def show_error(self, error):
        self._menu.title = 'Matryx - Error'
        self.set_label('Error:' + error)

    def show_message(self, message):
        self._menu.title = 'Matryx - Status'
        self.set_label(message)

    def set_label(self, text):
        self._label.text_value = text
        self._plugin.open_menu(self._menu)
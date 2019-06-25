import nanome

class Confirm:
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        self._menu = nanome.ui.Menu.io.from_json('menus/json/confirm.json')
        self._menu.register_closed_callback(on_close)

        self._description = self._menu.root.find_node('Description').get_content()
        self._button_cancel = self._menu.root.find_node('No').get_content()
        self._button_cancel.register_pressed_callback(on_close)
        self._button_confirm = self._menu.root.find_node('Yes').get_content()

    def open_menu(self, text, callback):
        self._description.text_value = text
        cb = lambda btn: callback()
        self._button_confirm.register_pressed_callback(cb)
        self._plugin.open_menu(self._menu)
import os
from functools import partial
import nanome
from nanome.util import Logs

class SettingsMenu:
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        self._network = 'ropsten'
        self._gas_price = '4'

        self._menu = nanome.ui.Menu.io.from_json('menus/json/settings.json')
        self._menu.register_closed_callback(on_close)

        self._button_confirm = self._menu.root.find_node('Confirm').get_content()
        self._button_confirm.register_pressed_callback(on_close)

        self._gas_price_value = self._menu.root.find_node('Gas Price Value').get_content()
        self._slider_gas_price = self._menu.root.find_node('Gas Slider').get_content()
        self._slider_gas_price.register_changed_callback(self.update_gas)
        self._slider_gas_price.register_released_callback(self.update_gas)

        self._slider_gas_price.current_value = 4
        self._gas_price_value.text_value = str(4)

        self._ln_network_buttons = self._menu.root.find_node('Network Buttons')

        self._prefab_network_item = self._menu.root.find_node('Network Button Prefab')
        self._buttons_network = []
        for network in ['mainnet', 'ropsten']:
            item = self._prefab_network_item.clone()
            item.network = network
            item.set_size_fixed(0.1)
            self._buttons_network.append(item)

            btn = item.get_content()
            btn.set_all_text(network)
            icon = item.find_node('Check Icon')
            icon.add_new_image(os.path.join(os.path.dirname(__file__), '..', 'images', 'checkmark.png'))
            icon.enabled = network == 'mainnet'
            btn.register_pressed_callback(partial(self.select_network, network))

            self._ln_network_buttons.add_child(item)

    def show_menu(self, button):
        self._plugin.open_menu(self._menu)

    def update_gas(self, slider):
        gas = int(self._slider_gas_price.current_value)
        self._gas_price = str(gas)
        self._gas_price_value.text_value = str(gas)
        self._plugin.refresh_menu()

    def select_network(self, network, button):
        self._plugin.set_to_refresh()

        self._network = network
        self._plugin._web3.set_network(network)

        for item in self._buttons_network:
            icon = item.find_node('Check Icon')
            icon.enabled = item.network == network

        self._plugin.refresh_menu()
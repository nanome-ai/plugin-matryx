import os
from functools import partial

import nanome
import utils
from nanome.util import Logs

from menus.select_winners.UpdateRoundMenu import UpdateRoundMenu

from web3 import Web3, HTTPProvider
import blockies

class OptionsMenu():
    def __init__(self, plugin, select_winners_menu, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/select_winners/options.json')
        menu.register_closed_callback(on_close)
        self._menu = menu

        self._menu_update_round = UpdateRoundMenu(plugin, select_winners_menu, on_close)
        self._menu_select_winners = select_winners_menu

        self._text = menu.root.find_node('Text').get_content()
        self._button_do_nothing = menu.root.find_node('Do Nothing').get_content()
        self._button_do_nothing.register_pressed_callback(self.do_nothing)
        self._button_update_round = menu.root.find_node('Start Round').get_content()
        self._button_update_round.register_pressed_callback(self._menu_update_round.show_menu)
        self._button_close_tournament = menu.root.find_node('Close Tournament').get_content()
        self._button_close_tournament.register_pressed_callback(self.close_tournament)

    def show_menu(self, button):
        self._plugin.open_menu(self._menu)

    def do_nothing(self, button):
        def callback():
            self._plugin.pop_menu_history(3)
            self._menu_select_winners.select_winners(0)

        text = 'You are about to send a transaction to confirm winners for this tournament. Are you sure you would like to do this?'
        self._plugin._menu_confirm.open_menu(text, callback)

    def close_tournament(self, button):
        def callback():
            self._plugin.pop_menu_history(3)
            self._menu_select_winners.select_winners(2)

        text = 'You are about to send a transaction to close the tournament. Are you sure you would like to do this?'
        self._plugin._menu_confirm.open_menu(text, callback)
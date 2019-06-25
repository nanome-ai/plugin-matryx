import os
from functools import partial

import nanome
import utils
from nanome.util import Logs

from web3 import Web3, HTTPProvider
import blockies

class OptionsMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/select_winners/options.json')
        menu.register_closed_callback(on_close)

        round_menu = nanome.ui.Menu.io.from_json('menus/json/update_round.json')
        round_menu.register_closed_callback(on_close)

        self._text = menu.root.find_node('Text').get_content()
        self._button_do_nothing = menu.root.find_node('Do Nothing').get_content()
        self._button_do_nothing.register_pressed_callback(self.do_nothing)
        self._button_update_round = menu.root.find_node('Start Round').get_content()
        self._button_update_round.register_pressed_callback(self.open_start_round)
        self._button_close_tournament = menu.root.find_node('Close Tournament').get_content()
        self._button_close_tournament.register_pressed_callback(self.close_tournament)

        self._menu = menu
        self._round_menu = round_menu

        self._tournament = None
        self._winners = []

    def show_menu(self, button):
        self._plugin.open_menu(self._menu)

    def do_nothing(self, button):
        text = 'You are about to send a transaction to confirm winners for this tournament. Are you sure you would like to do this?'
        callback = lambda: Logs.debug('we did nothing. yeet.')
        self._plugin._menu_confirm.open_menu(text, callback)

    def open_start_round(self, button):
        self._plugin.open_menu(self._round_menu)
        pass

    def close_tournament(self, button):
        text = 'You are about to send a transaction to close the tournament. Are you sure you would like to do this?'
        callback = lambda: Logs.debug('we closed the tournament. yeet.')
        self._plugin._menu_confirm.open_menu(text, callback)
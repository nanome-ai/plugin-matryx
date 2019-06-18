import requests
from functools import partial

import nanome
import utils
from nanome.util import Logs

class CreateTournamentMenu:
    def __init__(self, _plugin, on_close):
        self._plugin = _plugin
        menu_create_tournament = nanome.ui.Menu.io.from_json('menus/json/createTournament.json')
        menu_create_tournament.register_closed_callback(on_close)
        self._menu_create_tournament = menu_create_tournament

    def new_tournament(self, button):
        Logs.debug('design time!')
        pass
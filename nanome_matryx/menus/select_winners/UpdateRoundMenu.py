import requests
from functools import partial
from datetime import datetime, timedelta
import calendar
import math

from components.Calendar import Calendar

import nanome
import utils
from nanome.util import Logs

class UpdateRoundMenu:
    def __init__(self, _plugin, select_winners_menu, on_close):
        self._plugin = _plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/select_winners/update_round.json')
        menu.register_closed_callback(on_close)
        self._menu = menu

        self._menu_select_winners = select_winners_menu

        self._button_create = menu.root.find_node('Confirm').get_content()
        self._button_create.register_pressed_callback(self.update_new_round)
        self._button_cancel = menu.root.find_node('Cancel').get_content()
        self._button_cancel.register_pressed_callback(on_close)

        self._input_bounty = menu.root.find_node('Bounty Input').get_content()

        left_container = menu.root.find_node('Start Cal Container')
        self._calendar_start = Calendar(_plugin, left_container)

        right_container = menu.root.find_node('End Cal Container')
        self._calendar_end = Calendar(_plugin, right_container)

        now = datetime.now()
        self._start_datetime = now
        self._end_datetime = now + timedelta(days=30)

        self._calendar_start.set_datetime(self._start_datetime)
        self._calendar_start.set_readonly(True)

        self._calendar_end.set_datetime(self._end_datetime)
        self._calendar_end.set_min_datetime(now + timedelta(hours=1))
        self._calendar_end.set_max_datetime(now + timedelta(days=365))
        self._calendar_end.register_changed_callback(self.update_round_end)

    def show_menu(self, button=None):
        self._plugin.open_menu(self._menu)

    def update_new_round(self, button):
        if not self._input_bounty.input_text:
            self._plugin._modal.show_error('please enter a round bounty')
            return

        round_info = (
            utils.date_to_timestamp(self._calendar_start._datetime),  # start
            utils.diff_seconds(self._start_datetime, self._end_datetime),  # duration
            60 * 60 * 24 * 7,  # review
            self._plugin._web3.to_wei(self._input_bounty.input_text)  # bounty
        )
        self._menu_select_winners.select_winners(1, round_info)

    def update_round_end(self, dt):
        self._end_datetime = dt
        self._plugin.refresh_menu()
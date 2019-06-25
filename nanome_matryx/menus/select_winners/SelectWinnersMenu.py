import os
from functools import partial

import nanome
import utils
from nanome.util import Logs

from menus.select_winners.OptionsMenu import OptionsMenu

from web3 import Web3, HTTPProvider
import blockies

class SelectWinnersMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json('menus/json/select_winners/select_winners.json')
        menu.register_closed_callback(on_close)

        self._menu_options = OptionsMenu(plugin, on_close)

        self._submissions_list = menu.root.find_node('Submissions List').get_content()
        self._prefab_submission_item = menu.root.find_node('Submission Item Prefab')

        self._button_continue = menu.root.find_node('Continue').get_content()
        self._button_continue.register_pressed_callback(self._menu_options.show_menu)

        self._menu = menu

        self._tournament = None
        self._winners = []

    def load_tournament(self, tournament, button=None):
        self._tournament = tournament
        self._submissions_list.items = []

        address, index = tournament['address'], tournament['round']['index']
        submissions = self._plugin._cortex.get_round(address, index)['submissions']

        for submission in submissions:
            clone = self._prefab_submission_item.clone()
            clone.submission = submission

            title_label = clone.find_node('Label').get_content()
            title_label.text_value = submission['title']

            slider = clone.find_node('Slider')
            slider.enabled = False
            slider.get_content().register_released_callback(self.update_winnings)

            btn_sub = clone.find_node('Button').get_content()
            btn_sub.register_pressed_callback(partial(self.toggle_submission, clone))

            icon = clone.find_node('Icon')
            icon.enabled = False
            icon.add_new_image(os.path.join(os.path.dirname(__file__), '../../checkmark.png'))

            self._submissions_list.items.append(clone)

        self._plugin.open_menu(self._menu)

    def toggle_submission(self, item, button=None):
        slider = item.find_node('Slider')
        slider.enabled = not slider.enabled
        item.find_node('Icon').enabled = slider.enabled

        self.update_winnings()

    def update_winnings(self, slider=None):
        bounty = self._tournament['round']['bounty']
        winners = []
        self._winners = []

        total = 0
        for item in self._submissions_list.items:
            slider = item.find_node('Slider')
            item.find_node('Winnings').get_content().text_value = ''

            if slider.enabled:
                amount = slider.get_content().current_value
                total += amount
                winners.append((amount, item))

        for amount, item in winners:
            mtx = utils.truncate(bounty * amount / total)

            winnings = item.find_node('Winnings').get_content()
            winnings.text_value = mtx + ' MTX'

            self._winners.append((mtx, item.submission['hash']))

        self._button_continue.unusable = total == 0

        self._plugin.refresh_menu()
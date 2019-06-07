import os
from datetime import datetime
import nanome
import utils
from nanome.util import Logs

from web3 import Web3, HTTPProvider
from eth_account import Account
import blockies

class TournamentMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        menu = nanome.ui.Menu.io.from_json("_tournament_menu.json")
        menu.register_closed_callback(on_close)

        self._title = menu.root.find_node('Title').get_content()
        self._author = menu.root.find_node('Author').get_content()

        self._bounty = menu.root.find_node('Bounty').get_content()
        self._time_remaining = menu.root.find_node('Time Remaining').get_content()
        self._description = menu.root.find_node('Description').get_content()

        self._round_label = menu.root.find_node('Round Label').get_content()
        self._round_bounty = menu.root.find_node('Round Bounty').get_content()

        self._round_decrement = menu.root.find_node('Round Decrement').get_content()
        self._round_decrement.register_pressed_callback(self.press_dec_round)
        self._round_increment = menu.root.find_node('Round Increment').get_content()
        self._round_increment.register_pressed_callback(self.press_inc_round)

        self._submission_list_node = menu.root.find_node('Submission List')
        self._submission_list = self._submission_list_node.get_content()
        self._no_submissions_node = menu.root.find_node('No Submissions')
        self._no_submissions = self._no_submissions_node.get_content()

        self._prefab_submission_item = menu.root.find_node('Submission Item Prefab')

        self._button_view_files = menu.root.find_node('Files Button').get_content()
        self._button_view_files.register_pressed_callback(self._plugin._menu_files.load_files)

        self._menu = menu

        self._round_index = None
        self._round_index_max = None

    def load_tournament(self, button):
        address = button.tournament['address']
        tournament = self._plugin._cortex.get_tournament(address)
        self._tournament = tournament
        self._round_index_max = tournament['round']['index']

        self._title.text_value = tournament['title']
        self._description.text_value = tournament['description']

        self._author.text_value = 'by ' + utils.short_address(tournament['owner'])
        self._bounty.text_value = '%d MTX' % tournament['bounty']

        ipfs_hash = 'QmRxTEdWyE9xpvdgwKc4CeRp87knjfP9Q3Rgi12ydTP3Mz' # tournament['ipfsFiles']
        self._button_view_files.ipfs_hash = ipfs_hash
        self._button_view_files.unusable = ipfs_hash == ''

        end_date = datetime.fromisoformat(tournament['round']['endDate'].replace("Z", "+00:00"))
        time_remaining = utils.time_until(end_date)
        time_remaining = time_remaining + ' remaining' if time_remaining != '' else 'tournament closed'
        self._time_remaining.text_value = time_remaining

        self.display_round(tournament['round'])

        self._plugin.open_menu(self._menu)

    def load_round(self):
        round = self._plugin._cortex.get_round(self._tournament['address'], self._round_index)
        self.display_round(round)
        self._plugin.refresh_menu()

    def display_round(self, round):
        self._round_index = round['index']

        self._round_decrement.unusable = self._round_index == 0
        self._round_increment.unusable = self._round_index == self._round_index_max

        self._round_label.text_value = 'Round %d' % (round['index'] + 1)
        self._round_bounty.text_value = '%d MTX' % round['bounty']

        self._submission_list.items = []

        submissions = round['submissions']
        self._no_submissions_node.enabled = len(submissions) == 0
        self._submission_list_node.enabled = len(submissions) > 0

        for submission in submissions:
            clone = self._prefab_submission_item.clone()
            clone.enabled = True

            btn = clone.get_content()
            btn.submission = submission

            title = clone.find_node('Submission Title').get_content()
            title.text_value = utils.ellipsis(submission['title'], 23)

            by = clone.find_node('Submission Owner').get_content()
            by.text_value = 'by ' + utils.short_address(submission['owner'])

            self._submission_list.items.append(clone)

    def press_dec_round(self, button):
        Logs.debug('bleep')
        self._round_index -= 1
        self.load_round()

    def press_inc_round(self, button):
        Logs.debug('bloop')
        self._round_index += 1
        self.load_round()
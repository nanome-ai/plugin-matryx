from functools import partial
from datetime import datetime

import nanome
import utils
from nanome.util import Logs

from contracts.MatryxTournament import MatryxTournament

class TournamentMenu():
    def __init__(self, plugin, on_close):
        self._plugin = plugin

        self._round_index = None
        self._round_index_max = None

        menu = nanome.ui.Menu.io.from_json('menus/json/tournament.json')
        menu.register_closed_callback(on_close)
        self._menu = menu

        self._title = menu.root.find_node('Title').get_content()
        self._author = menu.root.find_node('Author').get_content()

        self._bounty = menu.root.find_node('Bounty').get_content()
        self._time_remaining = menu.root.find_node('Time Remaining').get_content()
        self._description = menu.root.find_node('Description').get_content()

        self._round_label = menu.root.find_node('Round Label').get_content()
        self._round_bounty = menu.root.find_node('Round Bounty').get_content()

        self._round_decrement = menu.root.find_node('Round Decrement').get_content()
        self._round_decrement.register_pressed_callback(partial(self.change_round, -1))
        self._round_increment = menu.root.find_node('Round Increment').get_content()
        self._round_increment.register_pressed_callback(partial(self.change_round, 1))

        self._menu_submit = nanome.ui.Menu.io.from_json('menus/json/create_submission.json')
        self._menu_submit.register_closed_callback(on_close)

        self._submission_list_node = menu.root.find_node('Submission List')
        self._submission_list = self._submission_list_node.get_content()
        self._no_submissions_node = menu.root.find_node('No Submissions')
        self._no_submissions = self._no_submissions_node.get_content()

        self._prefab_submission_item = menu.root.find_node('Submission Item Prefab')

        self._button_view_files = menu.root.find_node('Files Button').get_content()
        self._button_create_sub = menu.root.find_node('Create Button').get_content()
        self._button_create_sub.register_pressed_callback(self._plugin._menu_creations.open_my_creations)

        self._menu_submission = nanome.ui.Menu.io.from_json('menus/json/submission.json')
        self._menu_submission.register_closed_callback(on_close)

        self._submission_title = self._menu_submission.root.find_node('Title').get_content()
        self._submission_creator = self._menu_submission.root.find_node('Creator').get_content()
        self._submission_date = self._menu_submission.root.find_node('Date').get_content()
        self._submission_description = self._menu_submission.root.find_node('Description').get_content()
        self._submission_view_files = self._menu_submission.root.find_node('View Files').get_content()

    def load_tournament(self, address, button):
        tournament = self._plugin._cortex.get_tournament(address)

        self._contract = MatryxTournament(self._plugin, address)
        self._tournament = tournament
        self._round_index_max = tournament['round']['index']

        self._title.text_value = tournament['title']
        self._description.text_value = tournament['description']

        self._author.text_value = 'by ' + utils.short_address(tournament['owner'])
        self._bounty.text_value = '%d MTX' % tournament['bounty']

        ipfs_hash = 'QmUV7wfHWoTJqk61K2A8XbQ6AS7ERQgyXa66X18MrpXrjz' #'QmWTje28788ZYSbJd4fpZtZM5spE5agCCcKHYdH5NtJMcZ' # tournament['ipfsFiles']
        self._button_view_files.unusable = ipfs_hash == ''
        callback = partial(self._plugin._menu_files.load_files, ipfs_hash)
        self._button_view_files.register_pressed_callback(callback)

        end_date = datetime.fromisoformat(tournament['round']['endDate'].replace('Z', '+00:00'))
        time_remaining = utils.time_until(end_date)
        time_remaining = time_remaining + ' remaining' if time_remaining != '' else 'tournament closed'
        self._time_remaining.text_value = time_remaining

        self.display_round(tournament['round'])

        self._plugin.open_menu(self._menu)

    def change_round(self, dir, button):
        self._round_index += dir
        self.load_round()

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
            btn.register_pressed_callback(partial(self.load_submission, submission['hash']))

            title = clone.find_node('Submission Title').get_content()
            title.text_value = utils.ellipsis(submission['title'], 23)

            by = clone.find_node('Submission Owner').get_content()
            by.text_value = 'by ' + utils.short_address(submission['owner'])

            self._submission_list.items.append(clone)

    def load_submission(self, submission_hash, button):
        submission = self._plugin._cortex.get_submission(submission_hash)

        self._submission_title.text_value = submission['title']
        self._submission_creator.text_value = 'by ' + utils.short_address(submission['owner'])
        self._submission_description.text_value = submission['description']
        self._submission_date.text_value = utils.timestamp_to_date(submission['timestamp'])

        callback = partial(self._plugin._menu_files.load_files, submission['commit']['ipfsContent'])
        self._submission_view_files.register_pressed_callback(callback)
        self._plugin.open_menu(self._menu_submission)

    def open_submit_menu(self, commit_hash, button):
        btn = self._menu_submit.root.find_node('Submit Button').get_content()
        btn.register_pressed_callback(partial(self.submit_to_tournament, commit_hash))
        self._plugin.open_menu(self._menu_submit)

    def submit_to_tournament(self, commit_hash, button):
        account = self._plugin._account.address

        is_entrant = self._contract.isEntrant(account)
        if not is_entrant:
            token = self._plugin._web3._token

            entry_fee = self._tournament['entryFee']
            balance = self._plugin._web3.get_mtx(account)
            allowance = self._plugin._web3.get_allowance(account)

            if balance < entry_fee:
                self._plugin._modal.show_error('Error: insufficient MTX balance')
                return
            elif allowance < entry_fee:
                if allowance != 0:
                    tx_hash = token.approve(self._web3._platform.address, 0)
                    Logs.debug('reset allowance tx', tx_hash)
                    self._plugin._web3.wait_for_tx(tx_hash)

                tx_hash = token.approve(self._web3._platform.address, entry_fee)
                Logs.debug('set allowance tx', tx_hash)
                self._plugin._web3.wait_for_tx(tx_hash)

            tx_hash = self._contract.enter()
            Logs.debug('enter tx', tx_hash)
            self._plugin._web3.wait_for_tx(tx_hash)

        title = self._menu_submit.root.find_node('Title Input').get_content().input_text
        description = self._menu_submit.root.find_node('Description Input').get_content().input_text
        ipfs_hash = self._plugin._cortex.upload_json({'title': title, 'description': description})

        tx_hash = self._contract.create_submission(ipfs_hash, commit_hash)
        Logs.debug('create tx', tx_hash)
        self._plugin._web3.wait_for_tx(tx_hash)


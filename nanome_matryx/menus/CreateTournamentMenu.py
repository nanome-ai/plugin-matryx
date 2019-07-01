import requests
from functools import partial
from datetime import datetime, timedelta
import calendar
import math

from components.Calendar import Calendar

import nanome
import utils
from nanome.util import Logs

class CreateTournamentMenu:
    def __init__(self, _plugin, on_close):
        self._plugin = _plugin
        menu_create_tournament = nanome.ui.Menu.io.from_json('menus/json/create_tournament.json')
        menu_create_tournament.register_closed_callback(on_close)
        self._menu_create_tournament = menu_create_tournament

        self._button_create = self._menu_create_tournament.root.find_node('Create').get_content()
        self._button_create.register_pressed_callback(self.create_tournament)
        self._button_cancel = self._menu_create_tournament.root.find_node('Cancel').get_content()
        self._button_cancel.register_pressed_callback(on_close)

        self._input_title = self._menu_create_tournament.root.find_node('Title Input').get_content()
        self._input_title.register_submitted_callback(partial(self.limit_bad_input, False, 90))
        self._input_description = self._menu_create_tournament.root.find_node('Description Input').get_content()
        self._input_description.register_submitted_callback(partial(self.limit_bad_input, False, 100))
        self._input_bounty = self._menu_create_tournament.root.find_node('Bounty Input').get_content()
        self._input_entry_fee = self._menu_create_tournament.root.find_node('Entry Fee Input').get_content()
        self._input_round_bounty = self._menu_create_tournament.root.find_node('Round Bounty Input').get_content()

        left_container = self._menu_create_tournament.root.find_node('Start Cal Container')
        self._calendar_start = Calendar(_plugin, left_container)
        self._calendar_start.register_changed_callback(partial(self.update_datetime, True))

        right_container = self._menu_create_tournament.root.find_node('End Cal Container')
        self._calendar_end = Calendar(_plugin, right_container)
        self._calendar_end.register_changed_callback(partial(self.update_datetime, False))

    def clear_and_open(self, button):
        self._input_title.input_text = 'Create a Small Molecule'
        self._input_description.input_text = 'Create a small molecule de novo'
        self._input_bounty.input_text = ''
        self._input_entry_fee.input_text = ''
        self._input_round_bounty.input_text = ''

        self.reset_datetime_pickers()

        self._plugin.open_menu(self._menu_create_tournament)

    def create_tournament(self, button):
        if not self.validate_all():
            return

        w3 = self._plugin._web3
        bounty = w3.to_wei(int(self._input_bounty.input_text))
        entry_fee = w3.to_wei(int(self._input_entry_fee.input_text))
        round_bounty = w3.to_wei(int(self._input_round_bounty.input_text))

        title = self._input_title.input_text
        description = self._input_description.input_text
        balance = self._plugin._web3.get_mtx(self._plugin._account.address)
        allowance = self._plugin._web3.get_allowance(self._plugin._account.address)
        start = self._start_datetime
        end = self._end_datetime

        if allowance < bounty:
            if allowance != 0:
                self._plugin._modal.show_message('Resetting token allowance...')
                tx_hash = token.approve(self._web3._platform.address, 0)
                self._plugin._web3.wait_for_tx(tx_hash)

            self._plugin._modal.show_message('Setting token allowance to bounty...')
            tx_hash = w3._token.approve(w3._platform.address, bounty)
            self._plugin._web3.wait_for_tx(tx_hash)

        self._plugin._modal.show_message('Uploading Tournament details...')
        ipfs_hash = self._plugin._cortex.upload_json({'title': title, 'description': description})

        self._plugin._modal.show_message('Creating your tournament...')
        tx_hash = self._plugin._web3._platform.create_tournament(ipfs_hash, bounty, entry_fee, round_bounty, start, end)
        self._plugin._web3.wait_for_tx(tx_hash)

        self._plugin._modal.show_message('Tournament creation successful.')
        self._plugin.update_account()

    def update_datetime(self, is_start, dt):
        if is_start:
            self._start_datetime = dt
            self._calendar_end.set_min_datetime(dt + timedelta(hours=1))
            self._calendar_end.set_max_datetime(dt + timedelta(days=365))
        else:
            self._end_datetime = dt

        self._plugin.refresh_menu()

    def validate_all(self):
        (valid, error) = self.validate_input(False, 3, 90, self._input_title)
        if not valid:
            self._plugin._modal.show_error('invalid title length: ' + error)
            return False

        (valid, error) = self.validate_input(False, 10, 100, self._input_description)
        if not valid:
            self._plugin._modal.show_error('invalid description length: ' + error)
            return False

        w3 = self._plugin._web3
        mtx_balance = w3.get_mtx(self._plugin._account.address)

        # validate bounty
        (valid, error) = self.validate_input(True, 1, mtx_balance, self._input_bounty)
        if not valid:
            self._plugin._modal.show_error('invalid bounty: ' + error)
            return False

        # validate round bounty
        bounty = int(self._input_bounty.input_text)
        (valid, error) = self.validate_input(True, 1, bounty, self._input_round_bounty)
        if not valid:
            self._plugin._modal.show_error('invalid round bounty: ' + error)
            return False

        # validate entry fee
        (valid, error) = self.validate_input(True, 0, math.inf, self._input_entry_fee)
        if not valid:
            self._plugin._modal.show_error('invalid entry fee: ' + error)
            return False

        # validate start date a different way
        if self._start_datetime - datetime.now() < timedelta(hours=-1):
            self._plugin._modal.show_error('start date cannot occur in the past')
            return False

        # validate end date a different way
        if self._end_datetime - self._start_datetime < timedelta(hours=1):
            self._plugin._modal.show_error('round must be at least an hour long')
            return False

        # validate round duration
        if self._end_datetime - self._start_datetime > timedelta(days=365):
            self._plugin._modal.show_error('round must not last longer than one year')
            return False

        return True

    def limit_bad_input(self, is_number, max_val, input_field):
        if not self.validate_input(is_number, 0, max_val, input_field)[0]:
            if is_number:
                input_field.input_text = str(max_val)
            else:
                input_field.input_text = input_field.input_text[:max_val]
        self._plugin.refresh_menu()

    def validate_input(self, is_number, min_val, max_val, input_field):
        val = input_field.input_text
        if is_number:
            try:
                val = int(val)
                if val > max_val or val < min_val:
                    return (False, 'too big' if val > max_val else 'too small')
            except ValueError:
                return (False, 'not a number')
        else:
            val = len(val)
            if val > max_val or val < min_val:
                return (False, 'too long' if val > max_val else 'too short')

        return (True, '')

    def reset_datetime_pickers(self):
        self._calendar_start.set_min_datetime(datetime.now())
        self._calendar_end.set_min_datetime(datetime.now())
        self._calendar_start.set_datetime(datetime.now())
        self._calendar_end.set_datetime(datetime.now() + timedelta(days=30))

        self._plugin.refresh_menu()
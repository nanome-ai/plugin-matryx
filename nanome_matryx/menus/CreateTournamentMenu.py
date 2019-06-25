import requests
from functools import partial
from datetime import datetime, timedelta
import calendar
import math

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

        self._inputfield_title = self._menu_create_tournament.root.find_node('Title Input').get_content()
        self._inputfield_title.register_submitted_callback(partial(self.limit_bad_input, False, 90))
        self._inputfield_description = self._menu_create_tournament.root.find_node('Description Input').get_content()
        self._inputfield_description.register_submitted_callback(partial(self.limit_bad_input, False, 100))
        self._inputfield_bounty = self._menu_create_tournament.root.find_node('Bounty Input').get_content()
        self._inputfield_bounty.register_submitted_callback(partial(self.limit_bad_input, True, 100))
        self._inputfield_entry_fee = self._menu_create_tournament.root.find_node('Entry Fee Input').get_content()
        self._inputfield_entry_fee.register_submitted_callback(partial(self.limit_bad_input, True, 100))

        self._start_calendar = self._menu_create_tournament.root.find_node('Start Calendar')
        self._start_datetime = datetime.now()
        self._end_calendar = self._menu_create_tournament.root.find_node('End Calendar')
        self._end_datetime = datetime.now() + timedelta(days=7)

        self._inputfield_start_month_year = self._start_calendar.find_node('Month Year').get_content()
        self._inputfield_start_month_year.register_submitted_callback(partial(self.set_round_date_from_text, True))
        self._button_right_arrow_start_calendar = self._start_calendar.find_node('Right Arrow').get_content()
        self._button_right_arrow_start_calendar.register_pressed_callback(partial(self.change_month, 1, True))
        self._button_left_arrow_start_calendar = self._start_calendar.find_node('Left Arrow').get_content()
        self._button_left_arrow_start_calendar.register_pressed_callback(partial(self.change_month, -1, True))

        self._inputfield_start_hour = self._start_calendar.find_node('Start Hour Input').get_content()
        self._inputfield_start_hour.register_submitted_callback(partial(self.set_round_details_time, self._start_datetime, True, True))
        self._inputfield_start_min = self._start_calendar.find_node('Start Minute Input').get_content()
        self._inputfield_start_min.register_submitted_callback(partial(self.set_round_details_time, self._start_datetime, True, False))

        self._button_start_inc_hour = self._start_calendar.find_node('Inc Hour Start').get_content()
        self._button_start_inc_hour.register_pressed_callback(partial(self.change_hour, 1, True))

        self._button_start_dec_hour = self._start_calendar.find_node('Dec Hour Start').get_content()
        self._button_start_dec_hour.register_pressed_callback(partial(self.change_hour, -1, True))

        self._button_start_inc_min = self._start_calendar.find_node('Inc Min Start').get_content()
        self._button_start_inc_min.register_pressed_callback(partial(self.change_min, 1, True))

        self._button_start_dec_min = self._start_calendar.find_node('Dec Min Start').get_content()
        self._button_start_dec_min.register_pressed_callback(partial(self.change_min, -1, True))

        self._button_start_AM_PM = self._start_calendar.find_node('AMPM').get_content()
        self._button_start_AM_PM.register_pressed_callback(partial(self.switch_am_pm, True))

        self._inputfield_end_month_year = self._end_calendar.find_node('Month Year').get_content()
        self._inputfield_end_month_year.register_submitted_callback(partial(self.set_round_date_from_text, False))
        self._button_right_arrow_end_calendar = self._end_calendar.find_node('Right Arrow').get_content()
        self._button_right_arrow_end_calendar.register_pressed_callback(partial(self.change_month, 1, False))
        self._button_left_arrow_end_calendar = self._end_calendar.find_node('Left Arrow').get_content()
        self._button_left_arrow_end_calendar.register_pressed_callback(partial(self.change_month, -1, False))

        self._inputfield_end_hour = self._end_calendar.find_node('End Hour Input').get_content()
        self._inputfield_end_hour.register_submitted_callback(partial(self.set_round_details_time, self._start_datetime, False, True))

        self._inputfield_end_min = self._end_calendar.find_node('End Minute Input').get_content()
        self._inputfield_end_min.register_submitted_callback(partial(self.set_round_details_time, self._start_datetime, False, False))


        self._button_end_inc_hour = self._end_calendar.find_node('Inc Hour End').get_content()
        self._button_end_inc_hour.register_pressed_callback(partial(self.change_hour, 1, False))

        self._button_end_dec_hour = self._end_calendar.find_node('Dec Hour End').get_content()
        self._button_end_dec_hour.register_pressed_callback(partial(self.change_hour, -1, False))

        self._button_end_inc_min = self._end_calendar.find_node('Inc Min End').get_content()
        self._button_end_inc_min.register_pressed_callback(partial(self.change_min, 1, False))

        self._button_end_dec_min = self._end_calendar.find_node('Dec Min End').get_content()
        self._button_end_dec_min.register_pressed_callback(partial(self.change_min, -1, False))

        self._button_end_AM_PM = self._end_calendar.find_node('AMPM').get_content()
        self._button_end_AM_PM.register_pressed_callback(partial(self.switch_am_pm, False))

        self._start_calendar_day_buttons = []
        self._end_calendar_day_buttons = []
        for i in range(1, 43):
            self._start_calendar_day_buttons.append(self._start_calendar.find_node('Day %d' % i))
            self._end_calendar_day_buttons.append(self._end_calendar.find_node('Day %d' % i))

    def clear_and_open(self, button):
        self._inputfield_title.input_text = 'Create a Small Molecule'
        self._inputfield_description.input_text = 'Create a small molecule de novo'
        self._inputfield_bounty.input_text = ''
        self._inputfield_entry_fee.input_text = ''

        self.reset_datetime_pickers()
        self.update_datetime_pickers(True, True, True, False)

        self.populate_buttons(self._start_calendar_day_buttons)
        self.populate_buttons(self._end_calendar_day_buttons)

        self._plugin.open_menu(self._menu_create_tournament)

    def create_tournament(self, button):
        if not self.validate_all():
            return

        w3 = self._plugin._web3
        bounty = w3.to_wei(int(self._inputfield_bounty.input_text), 'ether')
        entry_fee = w3.to_wei(int(self._inputfield_entry_fee.input_text), 'ether')

        # show modal for setting allowance...
        self._plugin._modal.show_message('Setting token allowance...')
        title = self._inputfield_title.input_text
        description = self._inputfield_description.input_text
        balance = self._plugin._web3.get_mtx(self._plugin._account.address)
        allowance = self._plugin._web3.get_allowance(self._plugin._account.address)
        start = self._start_datetime
        end = self._end_datetime

        Logs.debug("bounty: %d, allowance: %d" % (bounty, allowance))

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
        tx_hash = self._plugin._web3._platform.create_tournament(ipfs_hash, bounty, entry_fee, start, end)
        Logs.debug('create tx', tx_hash)
        self._plugin._web3.wait_for_tx(tx_hash)
        self._plugin._modal.show_message('Tournament creation successful.')

    def validate_all(self):
        (valid, error) = self.validate_input(False, 3, 90, self._inputfield_title)
        if not valid:
            self._plugin._modal.show_error('invalid title length: ' + error)
            return False

        (valid, error) = self.validate_input(False, 10, 100, self._inputfield_description)
        if not valid:
            self._plugin._modal.show_error('invalid description length: ' + error)
            return False

        w3 = self._plugin._web3
        mtx_balance = w3.get_mtx(self._plugin._account.address)

        # validate bounty
        (valid, error) = self.validate_input(True, 1, mtx_balance, self._inputfield_bounty)
        if not valid:
            self._plugin._modal.show_error('invalid bounty: ' + error)
            return False

        # validate entry fee
        (valid, error) = self.validate_input(True, 0, math.inf, self._inputfield_entry_fee)
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

    def populate_buttons(self, is_start):
        dt = self._start_datetime if is_start else self._end_datetime
        cal_btns = self._start_calendar_day_buttons if is_start else self._end_calendar_day_buttons

        first_day, num_days = calendar.monthrange(dt.year, dt.month)
        first_day = (first_day + 1) % 7

        min_date = datetime.today().date()
        max_date = (datetime.today() + timedelta(days=365)).date()

        for i in range(0, 42):
            btn = cal_btns[i].get_content()
            if i < first_day or i >= first_day + num_days:
                btn.unusable = True
                btn.set_all_text('')
            else:
                day = 1 + i - first_day
                btn.set_all_text(str(day))
                btn.selected = day == dt.day
                date = datetime(dt.year, dt.month, day, 0, 0)
                btn.unusable = date.date() < min_date or date.date() > max_date
                btn.register_pressed_callback(partial(self.set_round_date, date, is_start))

    def set_round_date(self, dt, is_start, button):
        if is_start:
            time = self._start_datetime.time()
            self._start_datetime = datetime.combine(dt.date(), time)
            self._inputfield_start_month_year.input_text = self._start_datetime.strftime("%B %Y")
        else:
            time = self._end_datetime.time()
            self._end_datetime = datetime.combine(dt.date(), time)
            self._inputfield_end_month_year.input_text = self._end_datetime.strftime("%B %Y")

        self.update_datetime_pickers(is_start, not is_start, True)
        self._plugin.refresh_menu()

    def set_round_date_from_text(self, is_start, button):
        update = True
        if is_start:
            txt = self._inputfield_start_month_year.input_text
            try:
                date = datetime.strptime(txt, '%B %Y').date()
            except Exception:
                update = False
                date = self._start_datetime
                self._plugin._modal.show_error('invalid date')
            sdt = self._start_datetime
            self._start_datetime = datetime(date.year, date.month, date.day, sdt.hour, sdt.minute)
        else:
            txt = self._inputfield_end_month_year.input_text
            try:
                date = datetime.strptime(txt, '%B %Y').date()
            except Exception:
                update = False
                date = self._end_datetime
                self._plugin._modal.show_error('invalid date')
            edt = self._end_datetime
            self._end_datetime = datetime(date.year, date.month, date.day, edt.hour, edt.minute)

        if update:
            self.update_datetime_pickers(is_start, not is_start, True)

    def set_round_details_time(self, dt, is_start, is_hour, field):
        self.limit_bad_input(False, 24, field)

        if is_start:
            dt = self._start_datetime
            if is_hour:
                self._start_datetime = datetime(dt.year, dt.month, dt.day, int(field.input_text), dt.minute)
            else:
                self._start_datetime = datetime(dt.year, dt.month, dt.day, dt.hour, int(field.input_text))
        else:
            dt = self._end_datetime
            if is_hour:
                self._end_datetime = datetime(dt.year, dt.month, dt.day, int(field.input_text), dt.minute)
            else:
                self._end_datetime = datetime(dt.year, dt.month, dt.day, dt.hour, int(field.input_text))

        self.update_datetime_pickers(is_start, not is_start, False)

    def change_month(self, dir, is_start, button):
        dt = self._start_datetime if is_start else self._end_datetime
        month = ((dt.month + dir - 1) % 12) + 1  # lol

        year_change = (dt.month == 1 and dir == -1) or (dt.month == 12 and dir == 1)
        year_inc = dir if year_change else 0

        if is_start:
            self._start_datetime = datetime(dt.year + year_inc, month, dt.day, dt.hour, dt.minute)
        else:
            self._end_datetime = datetime(dt.year + year_inc, month, dt.day, dt.hour, dt.minute)

        self.update_datetime_pickers(is_start, not is_start, True)

    def change_hour(self, dir, is_start, button):
        day_before = self._start_datetime.day
        if is_start:
            self._start_datetime += dir * timedelta(hours=1)
        else:
            self._end_datetime += dir * timedelta(hours=1)
        day_after = self._start_datetime.day

        update_buttons = day_before != day_after
        self.update_datetime_pickers(is_start, not is_start, update_buttons)

    def change_min(self, dir, is_start, button):
        day_before = self._start_datetime.day
        if is_start:
            self._start_datetime += dir * timedelta(minutes=1)
        else:
            self._end_datetime += dir * timedelta(minutes=1)
        day_after = self._start_datetime.day

        update_buttons = day_before != day_after
        self.update_datetime_pickers(is_start, not is_start, update_buttons)

    def switch_am_pm(self, is_start, button):
        if is_start:
            dt = self._start_datetime
            self._start_datetime = datetime(dt.year, dt.month, dt.day, (dt.hour + 12) % 24, dt.minute)
            self._button_start_AM_PM.set_all_text(dt.strftime('%p'))
        else:
            dt = self._end_datetime
            self._end_datetime = datetime(dt.year, dt.month, dt.day, (dt.hour + 12) % 24, dt.minute)
            self._button_end_AM_PM.set_all_text(dt.strftime('%p'))

        self.update_datetime_pickers(is_start, not is_start, False)

    def reset_datetime_pickers(self):
        self._start_datetime = datetime.now()
        self._end_datetime = datetime.now() + timedelta(days=14)

    def update_datetime_pickers(self, update_start, update_end, update_buttons, update_menu=True):
        if self._start_datetime < datetime.now():
            update_start = True
            self._start_datetime = datetime.now()

        if self._end_datetime - self._start_datetime < timedelta(hours=1):
            update_end = True
            self._end_datetime = self._start_datetime + timedelta(hours=1)

        if self._end_datetime - self._start_datetime > timedelta(days=365):
            update_end = True
            self._end_datetime = self._start_datetime + timedelta(days=365)

        sdt = self._start_datetime
        edt = self._end_datetime

        if update_start:
            self._inputfield_start_month_year.input_text = sdt.strftime("%B %Y")
            self._inputfield_start_hour.input_text = sdt.strftime('%I')
            self._inputfield_start_min.input_text = sdt.strftime('%M')
            self._button_start_AM_PM.set_all_text(sdt.strftime('%p'))
            if update_buttons:
                self.populate_buttons(True)
        if update_end:
            self._inputfield_end_month_year.input_text = self._end_datetime.strftime("%B %Y")
            self._inputfield_end_hour.input_text = edt.strftime('%I')
            self._inputfield_end_min.input_text = edt.strftime('%M')
            self._button_end_AM_PM.set_all_text(edt.strftime('%p'))
            if update_buttons:
                self.populate_buttons(False)

        if update_menu:
            self._plugin.refresh_menu()
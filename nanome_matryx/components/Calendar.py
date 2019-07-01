import requests
from functools import partial
from datetime import datetime, timedelta
import calendar
import math

import nanome
import utils
from nanome.util import Logs

class Calendar:
    def __init__(self, _plugin, container):
        self._plugin = _plugin

        menu = nanome.ui.Menu.io.from_json('components/json/calendar.json')
        self._menu = menu

        calendar = menu.root.find_node('Container')

        self._datetime = datetime.now()
        self._min_datetime = datetime.fromtimestamp(0)
        self._max_datetime = datetime.fromtimestamp(1e10)  # lell

        self._input_month_year = calendar.find_node('Month Year').get_content()
        self._input_month_year.register_submitted_callback(self.set_date_from_text)
        self._button_inc_month = calendar.find_node('Inc Month').get_content()
        self._button_inc_month.register_pressed_callback(partial(self.change_month, 1))
        self._button_dec_month = calendar.find_node('Dec Month').get_content()
        self._button_dec_month.register_pressed_callback(partial(self.change_month, -1))

        self._input_hour = calendar.find_node('Hour Input').get_content()
        self._input_hour.register_submitted_callback(partial(self.set_time, self._datetime, True))
        self._input_min = calendar.find_node('Minute Input').get_content()
        self._input_min.register_submitted_callback(partial(self.set_time, self._datetime, False))

        self._button_inc_hour = calendar.find_node('Inc Hour').get_content()
        self._button_inc_hour.register_pressed_callback(partial(self.change_hour, 1))
        self._button_dec_hour = calendar.find_node('Dec Hour').get_content()
        self._button_dec_hour.register_pressed_callback(partial(self.change_hour, -1))

        self._button_inc_min = calendar.find_node('Inc Min').get_content()
        self._button_inc_min.register_pressed_callback(partial(self.change_min, 1))
        self._button_dec_min = calendar.find_node('Dec Min').get_content()
        self._button_dec_min.register_pressed_callback(partial(self.change_min, -1))

        self._button_AM_PM = calendar.find_node('AMPM Button').get_content()
        self._button_AM_PM.register_pressed_callback(partial(self.toggle_am_pm))

        self._label_AM_PM = calendar.find_node('AMPM Label').get_content()

        self._calendar_day_buttons = []
        for i in range(1, 43):
            self._calendar_day_buttons.append(calendar.find_node('Day %d' % i))

        self._readonly = False

        container.add_child(calendar)
        self.populate_buttons()

    def populate_buttons(self):
        dt = self._datetime
        cal_btns = self._calendar_day_buttons

        first_day, num_days = calendar.monthrange(dt.year, dt.month)
        first_day = (first_day + 1) % 7

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
                btn.register_pressed_callback(partial(self.set_date, date))

                min_date, max_date = self._min_datetime.date(), self._max_datetime.date()
                invalid_date = date.date() < min_date or date.date() > max_date
                btn.unusable = not btn.selected and (self._readonly or invalid_date)

    def _datetime_callback(self, dt):
        pass

    def register_changed_callback(self, func):
        self._datetime_callback = func

    def set_readonly(self, readonly):
        self._readonly = readonly

        self._button_inc_month.unusable = readonly
        self._button_dec_month.unusable = readonly
        self._button_inc_hour.unusable = readonly
        self._button_dec_hour.unusable = readonly
        self._button_inc_min.unusable = readonly
        self._button_dec_min.unusable = readonly
        self._button_AM_PM.unusable = readonly

        self.populate_buttons()

    def set_datetime(self, dt):
        self._datetime = dt
        self.update_datetime(True)

    def set_min_datetime(self, dt):
        self._min_datetime = dt
        self.update_datetime(False)

    def set_max_datetime(self, dt):
        self._max_datetime = dt
        self.update_datetime(False)

    def set_date(self, dt, button):
        time = self._datetime.time()
        self._datetime = datetime.combine(dt.date(), time)
        self._input_month_year.input_text = self._datetime.strftime("%B %Y")

        self.update_datetime(True)

    def set_date_from_text(self, button):
        update = True
        txt = self._input_month_year.input_text

        try:
            date = datetime.strptime(txt, '%B %Y').date()
            sdt = self._datetime
            self._datetime = datetime(date.year, date.month, date.day, sdt.hour, sdt.minute)
        except Exception:
            update = False
            self._plugin._modal.show_error('invalid date')

        if update:
            self.update_datetime(True)

    def set_time(self, dt, is_hour, field):
        dt = self._datetime
        value = int(field.input_text)

        if is_hour:
            value = min(11, max(0, value % 12))
            # keep am pm from before
            if dt.hour >= 12: value += 12
            self._datetime = datetime(dt.year, dt.month, dt.day, value, dt.minute)
        else:
            value = min(59, max(0, value))
            self._datetime = datetime(dt.year, dt.month, dt.day, dt.hour, value)

        self.update_datetime(False)

    def change_month(self, dir, button):
        dt = self._datetime
        month = ((dt.month + dir - 1) % 12) + 1  # lol

        year_change = (dt.month == 1 and dir == -1) or (dt.month == 12 and dir == 1)
        year_inc = dir if year_change else 0

        self._datetime = datetime(dt.year + year_inc, month, dt.day, dt.hour, dt.minute)

        self.update_datetime(True)

    def change_hour(self, dir, button):
        day_before = self._datetime.day
        self._datetime += dir * timedelta(hours=1)
        day_after = self._datetime.day

        update_buttons = day_before != day_after
        self.update_datetime(update_buttons)

    def change_min(self, dir, button):
        day_before = self._datetime.day
        self._datetime += dir * timedelta(minutes=1)
        day_after = self._datetime.day

        update_buttons = day_before != day_after
        self.update_datetime(update_buttons)

    def toggle_am_pm(self, button):
        dt = self._datetime
        self._datetime = datetime(dt.year, dt.month, dt.day, (dt.hour + 12) % 24, dt.minute)
        self._label_AM_PM.text_value = dt.strftime('%p')

        self.update_datetime(False)

    def update_datetime(self, update_buttons):
        dt = min(self._max_datetime, max(self._min_datetime, self._datetime))
        update_buttons |= dt != self._datetime
        self._datetime = dt

        self._input_month_year.input_text = dt.strftime("%B %Y")
        self._input_hour.input_text = dt.strftime('%I')
        self._input_min.input_text = dt.strftime('%M')
        self._label_AM_PM.text_value = dt.strftime('%p')

        if not self._readonly:
            self._button_inc_month.unusable = dt.month == self._max_datetime.month and dt.year == self._max_datetime.year
            self._button_dec_month.unusable = dt.month == self._min_datetime.month and dt.year == self._min_datetime.year

            self._button_inc_hour.unusable = dt + timedelta(hours=1) > self._max_datetime
            self._button_dec_hour.unusable = dt - timedelta(hours=1) < self._min_datetime

            self._button_inc_min.unusable = dt + timedelta(minutes=1) > self._max_datetime
            self._button_dec_min.unusable = dt - timedelta(minutes=1) < self._min_datetime

        if update_buttons:
            self.populate_buttons()

        self._datetime_callback(dt)
import re
from datetime import datetime, timezone
from nanome.util import Logs
from math import inf

def short_address(address):
    return address[:6] + '...' + address[-4:]

def time_until(the_time):
    time = (the_time - datetime.now(timezone.utc)).total_seconds()

    if time < 0:
        return ''

    units = [(60, 's'), (60, 'm'), (24, 'h'), (7, 'd'), (52, 'w'), (inf, 'y')]

    for amount, label in units:
        if time < amount:
            return str(int(time)) + label
        time = time / amount

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('on %b %d, %Y at %I:%M %p')

def file_size(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    i = 0
    while size > 1024:
        size = size / 1024
        i += 1

    return truncate(size) + units[i]

def truncate(num, precision=2):
    val = '%.*f' % (precision, num)
    return re.sub('\.?0+$', '', val)

def ellipsis(text, length=55):
    return text[:length] + ('...' if len(text) > length else '')
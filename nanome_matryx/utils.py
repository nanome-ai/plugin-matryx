import re
from datetime import datetime, timezone
from nanome.util import Logs

def short_address(address):
    return address[:6] + '...' + address[-4:]

def time_until(the_time):
    time_difference = the_time - datetime.now(timezone.utc)
    time = time_difference.total_seconds()

    if time < 0:
        return ''

    unitlabels = ["s", "m", "h", "d", "w", "y"]
    unitamounts = [60, 60, 24, 7, 52]

    i = 0
    for x in unitlabels:
        if time < unitamounts[i]:
            break
        time = time / unitamounts[i]
        i += 1

    return str(int(time)) + unitlabels[i]

def truncate(num):
    val = '%.2f' % num
    return re.sub('\.?0+$', '', val)

def ellipsis(text, length=55):
    return text[:length] + ('...' if len(text) > length else '')
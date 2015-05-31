import sys
import os
import datetime

if not "--run" in sys.argv:
        # Only run at the end of a LUCID run
        delta = datetime.date.today() - datetime.date(2015, 1, 24) # Give a bit of space to sort things out... Should this be 23?
        diff =  delta.days % 8
        if not diff == 0:
                sys.exit(0)

        start_date = datetime.date.today() - datetime.timedelta(days=4) # Again, maybe should be 4 but would be a bit tight
else:
        start_date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

days = []

template = open("download-template.x").read()
template = template.replace("{DAY1}", days[0])
template = template.replace("{DAY2}", days[1])
template = template.replace("{DAY3}", days[2])

temp_file = open("/tmp/sstl-download.x", "w")
temp_file.write(template)


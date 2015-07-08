# A standalone module for quickly converting LUCID data files

import os
import sys
import numpy as np
from lucid_utils.lucidreader import LucidFile
from lucid_utils import telemetry, frameplot
import sqlite3
from datetime import datetime, timedelta, date

def get_run(dt):
	date_str = dt[0:10]
	date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
	diff = date_obj - date(2014, 12, 19)
	diff = diff.days % 8
	new_date = date_obj - timedelta(days=diff)
	#print new_date	
	return new_date.strftime("%Y-%m-%d")

INPUT_FOLDER = sys.argv[1] + "/"
OUTPUT_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/../xyc/"

files = []
# Read in a list of files from the specified folder
try:
	for root, dirs, sfiles in os.walk(INPUT_FOLDER):
		for sfile in sfiles:
			# Check whether the file follows the naming format
			if sfile[0:5] == "T1_LU":
				files.append(root + "/" + sfile)
	#print files

except:
	# The folder doesn't exist
	print "The input folder does no exist"
	sys.exit(1)
	
# Set up a database connection for use throughout
conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + "/../../data_browser.db")
c = conn.cursor()
	
# Loop through each file and import it
for filename in files:
	print "Processing data file", filename
	# Convert the filename into a readable datetime string
	fields = filename.split("_")
	file_id, f_date, f_time = fields[2], fields[3], fields[4]
	filename_datetime = f_date[0:4] + "-" + f_date[4:6] + "-" + f_date[6:8] + " " + f_time[0:2] + "." + f_time[2:4]
	# Check whether the data run already has a folder
	if not os.path.isdir(OUTPUT_FOLDER + get_run(filename_datetime)):
		os.mkdir(OUTPUT_FOLDER + get_run(filename_datetime))
	# Check whether this dataset has been imported already
	if os.path.isdir(OUTPUT_FOLDER + get_run(filename_datetime) + "/" + file_id):
		print "This file appears to have been imported already, skipping"
		continue
	current_base = OUTPUT_FOLDER + get_run(filename_datetime) + "/" + file_id
	# Create a folder to hold the data
	os.mkdir(current_base)

	# Open up the file and start reading in frames
	lf = LucidFile(filename)
	# Set up variables to hold the details of the first frame for the database
	first_frame = True
	first_timestamp = 0
	# Loop through each frame and write it to a text file
	for i in range(lf.num_frames - 1):
		print "\tProcessing frame", i
		frame = lf.get_frame(i)
		if first_frame:
			first_timestamp = frame.timestamp
			first_frame = False
		for j in range(5):
			if lf.active_detectors[j]:
				if frame.channels[j] != None:
					channel = frame.channels[j]
				else:
					channel = np.zeros((256, 256))
				f = open(current_base + "/frame" + str(i + 1) + "c" + str(j) + ".txt", "w")
				frameplot.get_image(channel, "RGB").save(current_base + "/frame" + str(i + 1) + "c" + str(j) + ".png")
				for x in range(256):
					for y in range(256):
						if channel[x][y]:
							f.write(str(x) + "\t" + str(y) + "\t" + str(channel[x][y]) + "\n")
		pos = telemetry.get_position("tds1.txt", frame.timestamp)
		c.execute("INSERT INTO frames VALUES(?, ?, ?, ?, ?);",
			(frame.timestamp, file_id, i + 1, pos.latitude, pos.longitude) )
	
	# Add the data file's details to the database
	print "\tProcessing database records"
	pos = telemetry.get_position("tds1.txt", first_timestamp)
	# Generate a comma-separated string of active detectors
	active_string = ""
	for i in range(5):
		if lf.active_detectors[i]:
			active_string += str(i) + ","
	# Trim off the final column
	active_string = active_string[:-1]
	c.execute("INSERT INTO data_files VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);",
		(file_id, filename, first_timestamp, pos.latitude, pos.longitude, lf.config, active_string, lf.num_frames, get_run(filename_datetime)) )
	conn.commit()

# Close the database connection
conn.commit()
conn.close()
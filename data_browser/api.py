import os
from django.http import HttpResponse
from django.db import connection
import json

def get_data_files(request):
	data_files = []
	c = connection.cursor()
	c.execute("SELECT * FROM data_files")
	rows = c.fetchall()
	for row in rows:
		data_file = {}
		data_file['id'] = str(row[0])
		data_file['timestamp'] = row[2]
		data_file['latitude'] = row[3]
		data_file['longitude'] = row[4]
		data_file['config'] = row[5]
		data_file['active_detectors'] = row[6]
		data_file['num_frames'] = row[7]
		data_file['run'] = row[8]
		data_files.append(data_file)
	return HttpResponse(json.dumps(data_files, indent=4), content_type = "text/plain")

def get_frames(request):
	frames = []
	c = connection.cursor()
	c.execute("SELECT * FROM frames WHERE data_file = ?", (request.GET['data_file'],))
	rows = c.fetchall()
	for row in rows[:-1]: # The last frame stored is often incomplete
		frame = {}
		frame['timestamp'] = row[0]
		frame['number'] = row[2]
		frame['latitude'] = row[3]
		frame['longitude'] = row[4]
		channels = {}
		run = request.GET['run']
		file_id = request.GET['data_file'].zfill(10)
		for channel in [0, 1, 3]:
			filename = os.path.dirname(os.path.abspath(__file__)) + "/xyc/" + run + "/" + file_id + "/frame" + str(frame['number']) + "c" + str(channel) + ".txt"			
			channels[channel] = open(filename).read()
		frame['channels'] = channels
		frames.append(frame)
	return HttpResponse(json.dumps(frames, indent=4), content_type = "text/plain")

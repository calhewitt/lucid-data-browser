from django.http import HttpResponse, HttpResponseRedirect
from django import template
import os
from django.db import connection
from datetime import date, datetime, timedelta
from lucid_utils import xycreader, frameplot
import numpy as np
from operator import itemgetter

def error4oh4(request):
	return HttpResponse("That data file could not be found!")

def get_run(dt):
	date_str = dt[0:10]
	date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
	diff = date_obj - date(2014, 12, 19)
	diff = diff.days % 8
	new_date = date_obj - timedelta(days=diff)
	#print new_date	
	return new_date.strftime("%Y-%m-%d")
	
def get_runs():
	# Grab a list of runs with their corresponding datasets from the database
	c = connection.cursor()
	c.execute("SELECT * FROM DATA_FILES")
	rows = c.fetchall()
	data_files = []
	runs = []
	for row in rows:
		# Extract each field from the appropriate position in the row
		file_dict = {}
		file_dict["id"] = row[0]
		file_dict["filename"] = row[1]
		file_dict["date"] = datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M')
		file_dict["timestamp"] = row[2]
		file_dict["latitude"] = row[3]
		file_dict["longitude"] = row[4]
		file_dict["config"] = row[5]
		file_dict["run"] = row[8]
		if not file_dict["run"] in runs:
			runs.append(file_dict["run"])
		data_files.append(file_dict)
	runs = sorted(runs)
	data_files = sorted(data_files, key=itemgetter('filename'))
	return data_files, runs

def main(request):
	# Initialise render dictionary
	page_vars = {}
	# Parse out the data filename and frame number
	file_id = request.path[6:] # Get rid of beginning slash
	page_vars["id"] = file_id
	# Get the details of the file from the database
	c = connection.cursor()
	c.execute("SELECT * FROM data_files WHERE Id = ?", (file_id,) )
	row = c.fetchone()
	if not row:
		# The file must not exist!
		return error4oh4(request)
	# And put them in the dictionary of values to be returned
	page_vars["run"] = row[8]
	page_vars["num_frames"] = row[7]
	
	# Check whether the user has specified a frame number
	if "frame" in request.GET:
		try:
			frame = int(request.GET["frame"])
		except:
			frame = 1
	else:
		frame = 1
	page_vars["frame"] = frame
	page_vars["data_files"], page_vars["runs"] = get_runs()
	# Finally, render the template and return it
	t = template.Template(open(os.path.dirname(os.path.abspath(__file__)) + "/templates/main.html").read())
	c = template.Context(page_vars)
	return HttpResponse(t.render(c))
	
def file_details(request):
	# This returns the details in the format supported by older versions...
	# Illogical but works, probably worth changing at some point
	return_str = ""
	id = request.GET["id"]
	c = connection.cursor()
	# Grab the details of the frames
	c.execute("SELECT * FROM frames WHERE data_file = ?", (id,) )
	count = 1
	# Add rows to the returned file, according to the legacy format...
	for row in c.fetchall():
		return_str += str(row[2]) + " " + str(row[0]) + " " + str(row[3]) + " " + str(row[4]) + "\n"
	return_str = return_str[:-1]
	
	return HttpResponse(return_str, content_type='text/plain')
	
def frame_image(request):
	use_preprocess = True
	if not "nopreproc" in request.GET.keys():
		# Get the appropriate data fields from the GET requests
		try:
			file_id, run, frame, channel = request.GET['file_id'].zfill(10), request.GET['run'], request.GET['frame'], request.GET['channel']
		except:
			# Some parameters could be missing...
			return HttpResponse("ERROR: Incorrect parameters supplied")
		filename = os.path.dirname(os.path.abspath(__file__)) + "/xyc/" + run + "/" + file_id + "/frame" + frame + "c" + channel + ".png"
		return HttpResponse(open(filename).read(), content_type="image/png")
	else:
		# Get the appropriate data fields from the GET requests
		try:
			file_id, run, frame, channel = request.GET['file_id'].zfill(10), request.GET['run'], request.GET['frame'], request.GET['channel']
		except:
			# Some parameters could be missing...
			return HttpResponse("ERROR: Incorrect parameters supplied")
		# Construct a file path from the arguments
		filename = os.path.dirname(os.path.abspath(__file__)) + "/xyc/" + run + "/" + file_id + "/frame" + frame + "c" + channel + ".txt"
		try:
			# ... and try to open it with lucidutils
			data = xycreader.read(filename)
		except:
			return HttpResponse("ERROR: That frame could not be found")
		# Convert the XYC data to an image and pipe it out
		img = frameplot.get_image(data, "RGB")
		response = HttpResponse(content_type="image/png")
		if "size" in request.GET.keys():
			size = request.GET["size"]
			img = img.resize((int(size), int(size)))
		img.save(response, "PNG")
		return response
		
def get_xyc(request):
	# Locate the appropriate XYC text files
	# Get the appropriate data fields from the GET requests
	try:
		file_id, run, frame, channel = request.GET['file_id'].zfill(10), request.GET['run'], request.GET['frame'], request.GET['channel']
	except:
		# Some parameters could be missing...
		return HttpResponse("ERROR: Incorrect parameters supplied")
	filename = os.path.dirname(os.path.abspath(__file__)) + "/xyc/" + run + "/" + file_id + "/frame" + frame + "c" + channel + ".txt"
	return HttpResponse(open(filename).read(), content_type='text/plain')
		
def root(request):
	# Find the id of the first data file
	c = connection.cursor()
	c.execute("SELECT * FROM data_files")
	row = c.fetchone()
	file_id = row[0]
	return HttpResponseRedirect("view/"+ str(file_id))
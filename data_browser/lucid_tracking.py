from django.http import HttpResponse, HttpResponseRedirect
from django import template
import os
import time
import sys
from lucid_utils import telemetry as tel

def main(request):
    page_vars = {}
    # Check for whether fullscreen mode is enabled
    if "embed" in request.GET.keys():
        page_vars["embed"] = True
    
    # Open the template file
    t = template.Template(open(os.path.dirname(os.path.abspath(__file__)) + "/templates/lucid_tracking.html").read())
    c = template.Context(page_vars)
    return HttpResponse(t.render(c))
    
    
def get_position(request):
    coordinates = tel.get_current_position("tds1.txt")
    return HttpResponse(str(coordinates.latitude) + "," + str(coordinates.longitude), content_type = "text/plain")
    
    
def get_line(request):
    return_text = ""
    
    ts = int(time.time())
    ts = ts - (50 * 60)

    for i in range(100):
    	pos = tel.get_position("tds1.txt", ts)
    	return_text += str(pos.latitude) + "," + str(pos.longitude)
    	if i < 99:
    		return_text += ";"
    	ts += 60

    return HttpResponse(return_text, content_type = "text/plain")
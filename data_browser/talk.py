from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
import time
import os
from django import template
from django.utils.html import escape

def main(request):
    c = connection.cursor()
    c.execute("SELECT * FROM talk;")
    messages = c.fetchall()
    messages.reverse()
    t = template.Template(open(os.path.dirname(os.path.abspath(__file__)) + "/templates/talk.html").read())
    c = template.Context({"messages": messages})
    return HttpResponse(t.render(c))

def submit(request):
    file, frame, message, user, run = escape(request.GET['file']), escape(request.GET['frame']), escape(request.GET['message']), escape(request.GET['user']), escape(request.GET['run'])
    ts = int(time.time())
    c = connection.cursor()
    c.execute("INSERT INTO talk VALUES(?, ?, ?, ?, ?, ?);", (ts, user, file, frame, message, run))
    return HttpResponseRedirect("./")

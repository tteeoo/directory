import os
import json
import requests
import humanize
from sys import argv

from flask_limiter import Limiter
from werkzeug.exceptions import HTTPException
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, url_for, request, send_from_directory, abort

DEBUG = False
DIRECTORY = "/home/theo/dev/repos/directory"

app = Flask(__name__, static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app)
limiter = Limiter(app, key_func=get_remote_address)

class Item:
    def __init__(self, name, url, directory, size_num=0):
        self.url = url
        self.name = name
        self.directory = directory
        if directory:
            self.name += "/"
        else:
            self.size = humanize.naturalsize(size_num, gnu=True)

@app.route("/")
@app.route("/directory")
@app.route("/directory/")
@limiter.limit("5/second")
def index():

    files = sorted(os.listdir(DIRECTORY))
    items = []
    for f in files:
        if f[0] == ".":
            continue
        if os.path.isdir(DIRECTORY + "/" + f):
            items.append(Item(f, "/directory/" + f, True)) 
        else:
            items.append(Item(f, "/file/" + f, False, size_num=os.path.getsize(DIRECTORY + "/" + f))) 

    return render_template("index.html", items=items)

@limiter.limit("5/second")
@app.route("/directory/<path:path>")
def directory(path):
    if ".." in path:
        abort(400)

    files = sorted(os.listdir(DIRECTORY + "/" + path))
    items = []
    for f in files:
        if f[0] == ".":
            continue
        if f[-1] == "/":
            f = f[:len(f)-1]
        if os.path.isdir(DIRECTORY + "/" + path + "/" + f):
            items.append(Item(f, "/directory/" + path + "/" + f, True)) 
        else:
            items.append(Item(f, "/file/" + path + "/" + f, False, size_num=os.path.getsize(DIRECTORY + "/" + path + "/" + f))) 

    return render_template("directory.html", items=items, path="/"+path, up="/directory"+"/"+"/".join((path).split("/")[:len((path).split("/"))-1]))

@limiter.limit("2/second")
@app.route("/file/<path:path>")
def file(path):
    if ".." in path:
        abort(400)

    return send_from_directory(DIRECTORY, path)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static/img", "favicon.ico")

if not DEBUG:
    @app.errorhandler(Exception)                                                                     
    def error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        return render_template("error.html", errno="HTTP Error: "+str(code))

if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0")

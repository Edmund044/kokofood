import requests
from flask import jsonify
import json
from flask import Flask, jsonify, render_template, request, url_for, redirect,session,flash
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploads'
app = Flask(__name__, template_folder='../templates',
            static_folder='../static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER    

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def make_request_to_convert_currency(amount1,  currency1, currency2):
    url = "https://api.apilayer.com/fixer/convert?to=" + \
        currency2+"&from="+currency1+"&amount="+amount1

    payload = {}
    headers = {
        "apikey": "Slyih31Y8eUs3dRJgZyPjaPCzVh8s01y"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    
    status_code = response.status_code
    res = json.loads(response.text)

    return res

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(image):
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return os.path.join(app.config['UPLOAD_FOLDER'], filename)
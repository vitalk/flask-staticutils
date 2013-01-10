#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template


def create_app(config):
    app = Flask(__name__)
    app.debug = True
    app.testing = True
    app.config['SECRET_KEY'] = 'so secret'

    for key, value in config.items():
        app.config[key] = value

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

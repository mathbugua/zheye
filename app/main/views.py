# coding=utf-8
from flask import render_template
from . import main


@main.route("/")
def index():
    return render_template("zheye.html", name="chenlong")

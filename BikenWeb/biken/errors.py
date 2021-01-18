""" Handle errors"""
from flask import Blueprint,flash,render_template, redirect, url_for,request


# Blueprint Configuration
err_bp = Blueprint(
    'err_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@err_bp.app_errorhandler(404)
def forbidden(e):
   return render_template('404.html'), 404

@err_bp.app_errorhandler(500)
def serverError(e):
   return render_template('500.html'), 500

@err_bp.app_errorhandler(Exception)
def defaultHandler(e):
   return render_template('defaultError.html'), e.code
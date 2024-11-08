from flask import render_template, request, session
from app import app
import werkzeug


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='404'), 404

@app.errorhandler(werkzeug.exceptions.HTTPException)
def internal_error(error):
    return render_template('500.html', title='500'), 500
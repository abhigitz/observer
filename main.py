"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
from flask import make_response
app = Flask(__name__)

from google.appengine.api import mail, users
from google.appengine.ext import deferred
import datetime

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

SA= ">moc.liamg@ztigihba<nimdA"
WHITE_LIST_USERS = set(w[::-1] for w in ['dnana.hsihsa', 'ztigihba', 'dnanatodhsihsa'])

def AuthorizeAndInform(user, pageName):
  if user.nickname().lower() not in WHITE_LIST_USERS:
    subject = "[SEWTRACKAPP] {} Page {} used the app at {}".format(pageName, user.nickname(), GetCurrentTimeAsString())
    SendDeferredMailToAdmins(subject, subject, subject)
  #TODO: restrict to authorized entries only
  return


def GetCurrentTimeObject():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)

def GetCurrentTimeAsString():
    return GetCurrentTimeObject().strftime("%Y-%b-%d: %H:%M:%S")

def SendDeferredMailToAdmins(subject, body, htmlBody=None):
    deferred.defer(SendInstantMailToAdmins, subject, body, htmlBody)
    return

def SendInstantMailToAdmins(subject, body, htmlBody=None):
    mail.send_mail_to_admins(SA[::-1], subject, body, html=htmlBody)

@app.route('/_ah/warmup')
def WarmupPage():
    return make_response("")

@app.route('/order')
def orderPage():
    """Payment page of the application."""
    AuthorizeAndInform(users.get_current_user(), "Order")
    return make_response(open('templates/order.html').read())


@app.route('/pmt')
def paymentPage():
    """Payment page of the application."""
    AuthorizeAndInform(users.get_current_user(), "PMT")
    return make_response(open('templates/pmt.html').read())

@app.route('/formC')
def PendingFormCPage():
    """Pending Form-C"""
    AuthorizeAndInform(users.get_current_user(), "FORMC")
    return make_response(open('templates/formC.html').read())

@app.route('/rawmat')
def RawMaterialAsOfNowPage():
    """Raw material as of now"""
    AuthorizeAndInform(users.get_current_user(), "RawMaterial")
    return make_response(open('templates/rawmat.html').read())

@app.route('/')
def indexPage():
    """First Page of the application."""
    AuthorizeAndInform(users.get_current_user(), "Main")
    return make_response(open('templates/index.html').read())

@app.route('/api/get-pending-orders-data', methods=['POST'])
def api_get_order_data():
    return make_response(open('static/dbs/order.json').read())

@app.route('/api/get-outstanding-pmt-data', methods=['POST'])
def api_get_pmt_data():
    return make_response(open('static/dbs/pmt.json').read())

@app.route('/api/get-km-pending-po-data', methods=['POST'])
def api_get_kmpo_data():
    return make_response(open('static/dbs/kmOrder.json').read())

@app.route('/api/get-formC-data', methods=['POST'])
def api_get_formc_data():
    return make_response(open('static/dbs/formC.json').read())

@app.route('/api/get-rawmaterial-data', methods=['POST'])
def api_get_rawmat_data():
    return make_response(open('static/dbs/rawmat.json').read())


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

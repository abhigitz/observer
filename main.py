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
    return

features = [
    {
      "featureName": "paymentPage",
      "servingUrl": "/pmt",
      "templatePath": "templates/pmt.html",
      "apiPath": "/api/get-outstanding-pmt-data",
      "methods": ["POST"],
      "jsonPath": 'static/dbs/pmt.json',
      },

    {
      "featureName": "PendingFormC",
      "servingUrl": "/formC",
      "templatePath": "templates/formC.html",
      "apiPath": "/api/get-formC-data",
      "methods": ["POST"],
      "jsonPath": 'static/dbs/formC.json',
      },

    {
      "featureName": "orders",
      "servingUrl": "/order",
      "templatePath": "templates/order.html",
      "apiPath": "/api/get-pending-orders-data",
      "methods": ["POST"],
      "jsonPath": 'static/dbs/order.json',
      },

    {
      "featureName": "RawMaterial",
      "servingUrl": "/rawmat",
      "templatePath": "templates/rawmat.html",
      "apiPath": "/api/get-rawmaterial-data",
      "methods": ["POST"],
      "jsonPath": 'static/dbs/rawmat.json',
      },

    ]

def create_handler(featureName, servingUrl, templatePath):
  def handler(featureName, templatePath):
    AuthorizeAndInform(users.get_current_user(), featureName)
    return make_response(open(templatePath).read())
  decorator = app.route(servingUrl)
  from functools import partial

  p = partial(handler, featureName=featureName, templatePath=templatePath)
  p.__name__ = "func_{}".format(featureName)

  return decorator(p)



def create_api_server(featureName, apiPath, methods, jsonPath):
  def api_server(jsonPath):
    return make_response(open(jsonPath).read())
  decorator = app.route(apiPath, methods=methods)
  from functools import partial

  p = partial(api_server, jsonPath=jsonPath)
  p.__name__ = "api_{}".format(featureName)

  return decorator(p)

def GenrateAllHandlersAndAPIServers():
  for f in features:
    #All the features have a similar structure, there is and html page and there is an api end point which is referred to retrieve the whole dataset. So we have defined all the 
    create_handler(f["featureName"], f["servingUrl"], f["templatePath"])
    create_api_server(f["featureName"], f["apiPath"], f["methods"], f["jsonPath"])


@app.route('/_ah/warmup')
def WarmupPage():
    return make_response("")


GenrateAllHandlersAndAPIServers()
create_handler("indexPage", "/", "templates/index.html")


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

# This is our wedding app

import os
import cgi
import urllib
from datetime import date
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

jinja_environment = jinja2.Environment(autoescape=False,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))    
names={'sholtebeck':'Steve','ingrahas':'Susy','mholtebeck':'Mark','aingrahamdwyer':'Andy','moxiemoo':'Janet'}
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def get_RSVP_list():
    rsvp_query = RSVP.query(ancestor=guestbook_key(DEFAULT_GUESTBOOK_NAME)).order(RSVP.nickname)
    rsvp_list = rsvp_query.fetch(100)
    return rsvp_list
    
def get_RSVP_count(rsvp_list):
    rsvp_count = 0
    for rsvp in rsvp_list:
        if rsvp.willAttend == "yes":
            rsvp_count += rsvp.attendees
    return rsvp_count

def globalVals(ctx):
    template_values= {
    "title": "Susy & Steve's Wedding",
    "date": "Easter Sunday, April 16 2017",   
    "time": "Mid-morning, about 8:30-10:30am HST",
    "attire":"Casual (dress for a beach park)",
    "location": "Magic Island Lagoon, Ala Moana Beach Park, Honolulu HI",
    "map_key": "AIzaSyBQC2Eyx7Z4ersTZg15-zfm73CXXAjcRtk",
    "yes": "You are attending&#9786;",
    "no": "&#9785; You are not attending",
    }
    # Get number of days until the big day
    template_values['days']=(date(2017,4,16)-date.today()).days
    if users.get_current_user() and names.get(users.get_current_user().nickname()):
        template_values['user'] = names[users.get_current_user().nickname()]
        template_values['url'] = users.create_logout_url(ctx.request.uri)
        template_values['url_linktext'] = 'Logout'
    else:
        template_values['user'] = ""
        template_values['url'] = users.create_login_url(ctx.request.uri)
        template_values['url_linktext'] = 'Login'
    return template_values
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values= globalVals(self)
        rsvp_list = get_RSVP_list()
        template_values['rsvplist']=rsvp_list
        rsvp_count=0
        for rsvp in rsvp_list:
            if rsvp.willAttend == "yes":
                rsvp_count += rsvp.attendees
            if rsvp.nickname == template_values['user']:
                template_values['msg']=template_values[rsvp.willAttend]
                template_values['rsvp'] = rsvp
        template_values['guestcount'] = rsvp_count
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

def guestbook_key(guestbookName=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbookName."""
    return ndb.Key('Guestbook', guestbookName)

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class RSVP(ndb.Model):
    """Models an individual RSVP entry."""
    nickname= ndb.StringProperty()
    name = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    state = ndb.StringProperty(indexed=False)
    zip = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    phone = ndb.StringProperty(indexed=False)
    note = ndb.TextProperty(indexed=False)
    willAttend= ndb.TextProperty(indexed=False)
    attendees = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Response(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('rsvp.html')
        guestbookName = self.request.get('guestbookName', DEFAULT_GUESTBOOK_NAME)
        rsvp_query = RSVP.query(ancestor=guestbook_key(guestbookName))
        rsvp_list = rsvp_query.fetch(100)
        pageVars = globalVals(self) 
        pageVars['rsvplist'] =  rsvp_list
        pageVars['title'] += ":RSVP"
        pageVars['guestcount'] = 0
        for rsvp in rsvp_list:
            if rsvp.willAttend == "yes":
                pageVars['guestcount'] += rsvp.attendees
            if rsvp.nickname == pageVars['user']:
                pageVars['rsvp'] = rsvp
        self.response.write(template.render(pageVars))

    def post(self):
        guestbookName = self.request.get('guestbookName', DEFAULT_GUESTBOOK_NAME)
        rsvp_key = self.request.get('nickname',users.get_current_user().nickname())
        rsvp = RSVP(parent=guestbook_key(guestbookName),id=rsvp_key)
        rsvp.name= self.request.get('name')
        rsvp.nickname = self.request.get('nickname')
        rsvp.email = self.request.get('email')
        rsvp.phone = self.request.get('phone')
        rsvp.address = self.request.get('address')
        rsvp.city= self.request.get('city')
        rsvp.state= self.request.get('state')
        rsvp.zip= self.request.get('zip')
        rsvp.willAttend= self.request.get('willAttend')
        rsvp.attendees = int(self.request.get('attendees'))
        rsvp.note = self.request.get('note')
        rsvp.put()
        self.redirect('/')


class MessageBoard(webapp2.RequestHandler):
    def get(self):
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbookName)).order(-Greeting.date)
        greetings = greetings_query.fetch(100)

        pageVars = globalVals(self)
        pageVars['greetings'] =  greetings
        pageVars['guestbookName'] = urllib.quote_plus(guestbookName)

        template = jinja_environment.get_template('templates/messageboard.html')
        self.response.write(template.render(pageVars))


class Registry(webapp2.RequestHandler):
    def get(self):
        pageVars = globalVals(self)
        template = jinja_environment.get_template('templates/registry.html')
        self.response.write(template.render(pageVars))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbookName))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        queryParams = {'guestbookName': guestbookName}
        self.redirect('/?' + urllib.urlencode(queryParams))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/registry', Registry),
    ('/messageboard', MessageBoard),
    ('/rsvp', Response),
    ('/responded', Response),
    ('/sign', Guestbook),
], debug=True)

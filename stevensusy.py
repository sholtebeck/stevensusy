# This is our wedding app

import os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

jinja_environment = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))    
names={'sholtebeck':'Steve','ingrahas':'Susy'}
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def globalVals(ctx):
    if users.get_current_user():
        url = users.create_logout_url(ctx.request.uri)
        linkText = 'Logout'
        notes = True;
        name = users.get_current_user().nickname()
    else:
        url = users.create_login_url(ctx.request.uri)
        linkText = 'Login'
        notes= False
        name = ""
    _get = ctx.request.GET
    return {
        'url': url,
        'linkText': linkText,
        'notes': notes,
        'name': name,
        'title': "Steve & Susy's Wedding",
        '_get': _get,
    }
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values= {	"title": "Steve & Susy's Wedding", 	"date": "Easter Sunday, April 16 2017",   
		"time":	"Mid-morning, about 8:30-10:30am HST",	"attire":"Casual (dress for a beach park)", "location":	"Magic Island Lagoon, Ala Moana Beach Park, Honolulu HI"	}
   
        if users.get_current_user() and names.get(users.get_current_user().nickname()):
            template_values['user'] = names[users.get_current_user().nickname()]
            template_values['url'] = users.create_logout_url(self.request.uri)
            template_values['url_linktext'] = 'Logout'
        else:
            template_values['user'] = ""
            template_values['url'] = users.create_login_url(self.request.uri)
            template_values['url_linktext'] = 'Login'
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
    author = ndb.UserProperty()
    fullName = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    note = ndb.TextProperty(indexed=False)
    willAttendWedding = ndb.TextProperty(indexed=False)
    willAttendReception = ndb.TextProperty(indexed=False)
    attendants = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Response(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/rsvp.html')
        pageVars = globalVals(self)
        pageVars['title'] = "RSVP"
        self.response.write(template.render(pageVars))

    def post(self):
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        rsvp = RSVP(parent=guestbook_key(guestbookName))

        if users.get_current_user():
            rsvp.author = users.get_current_user()

        rsvp.fullName = self.request.get('fullName')
        rsvp.nickname = self.request.get('nickname')
        rsvp.email = self.request.get('email')
        rsvp.willAttendWedding = self.request.get('willAttendWedding')
        rsvp.willAttendReception = self.request.get('willAttendReception')
        rsvp.attendants = int(self.request.get('attendants'))
        rsvp.note = self.request.get('note')
        rsvp.put()
        self.redirect('/?msg=Thank you for submitting your RSVP')



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

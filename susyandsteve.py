# This is our wedding app

import os
import cgi
import urllib
import jinja2
import webapp2
from datetime import date
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras import sessions

app_name='susyandsteve'
config={'webapp2_extras.sessions' : {'secret_key': app_name } }
jinja_environment = jinja2.Environment(autoescape=False,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))    
names={'sholtebeck':'Steve','ingrahas':'Susy','mholtebeck':'Mark','aingrahamdwyer':'Andy','moxiemoo':'Janet'}

def get_Nickname(input):
    (name,domain)=input.split('@')
    if (domain == 'gmail.com'):
        output = name       
    return output

def get_RSVP_list():
    rsvp_query = RSVP.query(ancestor=login_key(app_name)).order(RSVP.nickname)
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
    "maybe": "You might be attending"
    }
    # Get number of days until the big day
    template_values['action']=ctx.request.get('action') 
    template_values['days']=(date(2017,4,17)-date.today()).days
    template_values['nickname']=ctx.session_store.get_session().get('nickname') 
    if users.get_current_user() and names.get(users.get_current_user().nickname()):
        template_values['nickname'] = names[users.get_current_user().nickname()]
        ctx.session['nickname'] = template_values['nickname']
    if template_values.get('nickname'):
        template_values['url'] = users.create_logout_url(ctx.request.uri)
    else:
        template_values['url'] = users.create_login_url(ctx.request.uri)
    return template_values

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
 
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()     
    
class MainPage(BaseHandler):
    def get(self):
        template_values= globalVals(self)
        rsvp_list = get_RSVP_list()
        template_values['rsvplist']=rsvp_list
        rsvp_count=0
        for rsvp in rsvp_list:
            if rsvp.willAttend == "yes":
                rsvp_count += rsvp.attendees
            if rsvp.nickname == template_values['nickname']:
                template_values['msg']=template_values[rsvp.willAttend]
                template_values['rsvp'] = rsvp
        template_values['guestcount'] = rsvp_count
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

def login_key(guestbookName=app_name):
    """Constructs a Datastore key for a Login entity with guestbookName."""
    return ndb.Key('Login', guestbookName)

class Login(ndb.Model):
    """Models an individual Login entry."""
    nickname = ndb.StringProperty(indexed=False)
    login_date = ndb.DateTimeProperty(auto_now_add=True)

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

class Response(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('rsvp.html')
        guestbookName = self.request.get('guestbookName', app_name)
        rsvp_query = RSVP.query(ancestor=login_key(guestbookName))
        rsvp_list = rsvp_query.fetch(100)
        pageVars = globalVals(self) 
        pageVars['rsvplist'] =  rsvp_list
        pageVars['title'] += ":RSVP"
        pageVars['guestcount'] = 0
        for rsvp in rsvp_list:
            if rsvp.willAttend == "yes":
                pageVars['guestcount'] += rsvp.attendees
            if rsvp.nickname == pageVars['nickname']:
                pageVars['rsvp'] = rsvp
        self.response.write(template.render(pageVars))

    def post(self):
        guestbookName = self.request.get('guestbookName', app_name)
        rsvp_key = self.request.get('nickname')
        rsvp = RSVP(parent=login_key(guestbookName),id=rsvp_key)
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

class LogMeInOrOut(BaseHandler):
    def get(self):
        nickname = self.request.get('nickname')
        if not nickname or nickname in ('Guest','undefined'):
            del self.session['nickname']
            self.redirect(users.create_logout_url('/'))
        else:
            guestbookName = self.request.get('guestbookName', app_name)
            login = Login(parent=login_key(guestbookName), id=nickname)
            login.nickname = nickname
            self.session['nickname'] = nickname
            login.put()
            self.redirect('/')
            

    def post(self):
        # Login the user and save in the session
        nickname = self.request.get('nickname')
        # If input is gmail (xxx@gmail.com), redirect to Google login page
        if nickname.find('@gmail.com'):
            self.redirect(self.request.get('url'))
        if nickname != 'Guest':
            guestbookName = self.request.get('guestbookName', app_name)
            login = Login(parent=login_key(guestbookName), id=nickname)
            login.nickname = nickname
            if users.get_current_user():
                login.nickname = users.get_current_user().nickname()
            self.session['nickname'] = nickname
            login.put()
        self.redirect('/')

        
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rsvp', Response),
    ('/login', LogMeInOrOut),
    ('/logout', LogMeInOrOut),
], config=config,debug=True)

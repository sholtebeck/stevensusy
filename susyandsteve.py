# This is our wedding app

import os
import cgi
import urllib
import jinja2
import webapp2
from datetime import date
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from webapp2_extras import sessions

app_name='susyandsteve'
config={'webapp2_extras.sessions' : {'secret_key': app_name } }
jinja_environment = jinja2.Environment(autoescape=False,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))    
names={'sholtebeck':'Steve','ingrahas':'Susy','mholtebeck':'Mark','aingrahamdwyer':'Andy','moxiemoo':'Janet'}

def num(value, yesorno):
    if yesorno=="yes":
        try:
            return int(value)
        except ValueError:
            return 0
    else:
        return 0

def get_Nickname(input):
    (name,domain)=input.split('@')
    if (domain == 'gmail.com'):
        output = name       
    return output

def get_RSVP_list():
    rsvp_query = RSVP.query(ancestor=login_key(app_name)).order(RSVP.date)
    rsvp_list = rsvp_query.fetch(100)
    return rsvp_list
    
def get_RSVP_count(rsvp_list):
    rsvp_count={"HI":0,"CA":0,"WI":0}
    for rsvp in rsvp_list:
        if rsvp.willAttend == "yes":
            rsvp_count['HI'] += max(rsvp.attendees,1)
        if rsvp.willAttendCA == "yes":
            rsvp_count['CA'] += max(rsvp.attendees,1)
        if rsvp.willAttendWI == "yes":
            rsvp_count['WI'] += max(rsvp.attendees,1)
    return rsvp_count

def globalVals(ctx):
    template_values= {
    "title": "Susy & Steve's Wedding Tour",
    "date": "Easter Sunday, April 16 2017",   
    "time": "Mid-morning (9:30am HST)",
    "attire":"Casual (dress for a beach park)",
    "location": "Magic Island Lagoon, Ala Moana Beach Park, Honolulu HI",
    "map_key": "AIzaSyBQC2Eyx7Z4ersTZg15-zfm73CXXAjcRtk",
    "methods": ["email","facebook","mail","text"],
    "yes": "You are attending",
    "no": "You are not attending",
    "maybe": "You might be attending",
    "emoti": {"yes":"&#9786;","no":"&#9785;","maybe":""},
    "sender":"Susy & Steve <us@susyandsteve.appspotmail.com>",
    "subject":"Thank You for your RSVP",
    "states":[ { "name": "Alabama", "code": "AL" }, { "name": "Alaska", "code": "AK" }, { "name": "Arizona", "code": "AZ" }, { "name": "Arkansas", "code": "AR" },
    { "name": "California", "code": "CA" }, { "name": "Colorado", "code": "CO" }, { "name": "Connecticut", "code": "CT" }, { "name": "Delaware", "code": "DE" },
    { "name": "District Of Columbia", "code": "DC" }, { "name": "Florida", "code": "FL" }, { "name": "Georgia", "code": "GA" },  { "name": "Hawaii", "code": "HI" }, 
    { "name": "Idaho", "code": "ID" }, { "name": "Illinois", "code": "IL" }, { "name": "Indiana", "code": "IN" },   { "name": "Iowa", "code": "IA" }, 
    { "name": "Kansas", "code": "KS" }, { "name": "Kentucky", "code": "KY" }, { "name": "Louisiana", "code": "LA" },
    { "name": "Maine", "code": "ME" }, { "name": "Maryland", "code": "MD" }, { "name": "Massachusetts", "code": "MA" }, { "name": "Michigan", "code": "MI" },
    { "name": "Minnesota", "code": "MN" }, { "name": "Mississippi", "code": "MS" }, { "name": "Missouri", "code": "MO" }, { "name": "Montana", "code": "MT" },
    { "name": "Nebraska", "code": "NE" }, { "name": "Nevada", "code": "NV" }, { "name": "New Hampshire", "code": "NH" }, { "name": "New Jersey", "code": "NJ" },
    { "name": "New Mexico", "code": "NM" }, { "name": "New York", "code": "NY" }, { "name": "North Carolina", "code": "NC" }, { "name": "North Dakota", "code": "ND" },
    { "name": "Ohio", "code": "OH" }, { "name": "Oklahoma", "code": "OK" }, { "name": "Oregon", "code": "OR" }, { "name": "Pennsylvania", "code": "PA" },
    { "name": "Puerto Rico", "code": "PR" }, { "name": "Rhode Island", "code": "RI" }, { "name": "South Carolina", "code": "SC" }, { "name": "South Dakota", "code": "SD" },
    { "name": "Tennessee", "code": "TN" }, { "name": "Texas", "code": "TX" }, { "name": "Utah", "code": "UT" }, { "name": "Vermont", "code": "VT" }, { "name": "Virginia", "code": "VA" },
    { "name": "Washington", "code": "WA" }, { "name": "West Virginia", "code": "WV" }, { "name": "Wisconsin", "code": "WI" }, { "name": "Wyoming", "code": "WY"    } ],
    "carriers": [ {"name":"Alltel","domain":"message.alltel.com"},{"name":"AT&T","domain":"message.alltel.com"},{"name":"Boost","domain":"myboostmobile.com"},
    {"name":"Sprint","domain":"messaging.sprintpcs.com"},{"name":"T-Mobile","domain":"tmomail.net"},{"name":"Verizon","domain":"vtext.com"},{"name":"Virgin","domain":"vmobl.com"}  ],
    "tour": True
    }
    # Get number of days until the big day
    template_values['action']=ctx.request.get('action') 
    template_values['days']=(date(2017,4,16)-date.today()).days
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
        template_values['rsvp_list']=rsvp_list
        template_values['rsvpcount']=get_RSVP_count(rsvp_list)
        rsvplist={"HI":[],"CA":[],"WI":[]}
        for rsvp in rsvp_list:
            rsvp_name=rsvp.name
            if rsvp.attendees>1:
                rsvp_name+="("+str(rsvp.attendees)+")"
            if rsvp.willAttend == "yes":
                rsvplist["HI"].append(rsvp_name)
            if rsvp.willAttendCA == "yes":
                rsvplist["CA"].append(rsvp_name)
            if rsvp.willAttendWI == "yes":
                rsvplist["WI"].append(rsvp_name)             
            if rsvp.nickname == template_values['nickname']:
                template_values['msg']=template_values[rsvp.willAttend]
                template_values['emoticon']=template_values['emoti'][rsvp.willAttend]
                template_values['rsvp'] = rsvp
        template_values['rsvplist'] = rsvplist
        template_values['guestcount'] = len(rsvplist.get("HI"))
        if template_values["nickname"] in names.keys() or template_values["nickname"] in names.values() :
            template_values["weddingparty"]="Yes"
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
    carrier = ndb.StringProperty(indexed=False)
    contactMethod = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    willAttendCA= ndb.TextProperty(indexed=False)
    willAttendWI= ndb.TextProperty(indexed=False)
   
class Response(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('rsvp.html')
        guestbookName = self.request.get('guestbookName', app_name)
        rsvp_query = RSVP.query(ancestor=login_key(guestbookName))
        rsvp_list = rsvp_query.fetch(100)
        pageVars = globalVals(self) 
        pageVars['rsvplist'] =  rsvp_list
        pageVars['title'] = "RSVP to " + pageVars['title']
        pageVars['guestcount'] = 0
        for rsvp in rsvp_list:
#            if rsvp.willAttend == "yes":
#                pageVars['guestcount'] += rsvp.attendees
            if rsvp.nickname == pageVars['nickname']:
                pageVars['rsvp'] = rsvp
        self.response.write(template.render(pageVars))

    def post(self):
        globalvals=globalVals(self)
        guestbookName = self.request.get('guestbookName', app_name)
        rsvp_key = self.request.get('nickname')
        if not rsvp_key or rsvp_key in ('None','Guest'):
            rsvp_key = self.request.get('name').split(" ")[0]
        rsvp = RSVP(parent=login_key(guestbookName),id=rsvp_key)
        rsvp.nickname = rsvp_key
        rsvp.name= self.request.get('name')
        rsvp.email = self.request.get('email')
        rsvp.phone = self.request.get('phone')
        rsvp.address = self.request.get('address')
        rsvp.city= self.request.get('city')
        rsvp.state= self.request.get('state')
        rsvp.zip= self.request.get('zip')
        rsvp.willAttend= self.request.get('willAttend')
        rsvp.willAttendCA= self.request.get('willAttendCA')
        rsvp.willAttendWI= self.request.get('willAttendWI')
        rsvp.attendees = num(self.request.get('attendees'), max(rsvp.willAttend, rsvp.willAttendCA,rsvp.willAttendWI))
        rsvp.note = self.request.get('note')
        rsvp.contactMethod = self.request.get('contactMethod')
        rsvp.carrier = self.request.get('carrier')
        rsvp.put()
        if rsvp.contactMethod=='text' and rsvp.carrier and rsvp.willAttend =='yes':
            message = mail.EmailMessage(sender=globalvals['sender'], subject=globalvals['subject'])
            message.to = rsvp.phone + "@" + rsvp.carrier
            message.bcc = "steve@susyandsteve.com"
            message.body = "Hi " + rsvp.nickname  + ". Thank you for attending our wedding. See you there! :)"
            message.send()
        if rsvp.contactMethod=='text' and rsvp.carrier and (rsvp.willAttendCA =='yes' or rsvp.willAttendWI =='yes'):
            message = mail.EmailMessage(sender=globalvals['sender'], subject=globalvals['subject'])
            message.to = rsvp.phone + "@" + rsvp.carrier
            message.bcc = "steve@susyandsteve.com"
            message.body = "Hi " + rsvp.nickname  + ". Thank you for joining our wedding tour. See you there! :)"
            message.send()
        elif rsvp.contactMethod=='email' and mail.is_email_valid(rsvp.email) and rsvp.willAttend in ('yes','no'):
            message = mail.EmailMessage(sender=globalvals['sender'], subject=globalvals['subject'])
            message.to = rsvp.name + " <" + rsvp.email + ">"
            message.bcc = "steve@susyandsteve.com"
            if globalvals.get('bcc'):
                message.bcc = globalvals['bcc']
            message.html = "Hi "+ rsvp.nickname + ",<p>Thank you for your RSVP. " + globalvals[rsvp.willAttend]+globalvals['emoti'][rsvp.willAttend] + "<p>Susy & Steve<br>http://susyandsteve.com"
            message.send()
        self.redirect('/login?nickname='+rsvp_key)

class LogMeInOrOut(BaseHandler):
    def get(self):
        nickname = self.request.get('nickname')
        if not nickname or nickname in ('Guest','None','undefined'):
            if self.session.get('nickname'):
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
        nickname = self.request.get('nickname').title()
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

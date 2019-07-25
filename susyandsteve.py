# This is our wedding site
import os
import cgi
import urllib
import jinja2
import webapp2
from datetime import date,datetime
from google.appengine.api import users,mail,memcache
from google.appengine.ext import ndb
from webapp2_extras import sessions
from skipflog import *

app_name='susyandsteve'
config={'webapp2_extras.sessions' : {'secret_key': app_name } }
jinja_environment = jinja2.Environment(autoescape=False,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))    
names={'sholtebeck':'Steve','ingrahas':'Susy','mholtebeck':'Mark','aingrahamdwyer':'Andy','moxiemoo':'Janet','janetid':'Janet' }

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
    rsvp_list = memcache.get("RSVP")
    if not rsvp_list:
        rsvp_query = RSVP.query(ancestor=login_key(app_name)).order(RSVP.date)
        rsvp_list = rsvp_query.fetch(100)
        memcache.add("RSVP", rsvp_list)
    return rsvp_list
    
def get_RSVP_count(rsvp_list):
    rsvp_count={}
    for state in ("CA","HI",'WI'):
        rsvp_count[state]={"count":0,"guestlist":[]}
    for rsvp in rsvp_list:
        rsvp_name=rsvp.name
        if rsvp.attendees>1:
            rsvp_name+="("+str(rsvp.attendees)+")"
        if rsvp.willAttend == "yes":
            rsvp_count["HI"]["guestlist"].append(rsvp_name)
            rsvp_count["HI"]["count"] += max(rsvp.attendees,1)
        if rsvp.willAttendCA == "yes":
            rsvp_count["CA"]["guestlist"].append(rsvp_name)
            rsvp_count["CA"]["count"] += max(rsvp.attendees,1)
        if rsvp.willAttendWI == "yes":
            rsvp_count["WI"]["guestlist"].append(rsvp_name)
            rsvp_count["WI"]["count"] += max(rsvp.attendees,1)
    return rsvp_count

def globalVals(ctx):
    template_values= {
    "title": "Susy & Steve's Wedding Tour",
    "date": "Easter Sunday, April 16 2017",   
    "time": "10:00am HST",
    "attire":"Casual (dress for a beach park)",
    "location": "Magic Island, Ala Moana Beach Park, Honolulu HI",
    "methods": ["email","facebook","mail","text"],
    "yes": "You are attending",
    "no": "You are not attending",
    "maybe": "You might be attending",
    "NA": "You could not attend",
    "emoti": {"yes":"&#9786;","no":"&#9785;","maybe":"","NA":""},
    "extras":["setup","cleanup","assisting","chairs","highchairs","boosters","song","food"],
    "request" : ctx.request,
    "sender":"Susy & Steve <us@susyandsteve.appspotmail.com>",
    "subject":"Thank You for your RSVP",
    "pages": [ {"name":"Tour","url":"/weddingtour"},  {"name":"RSVP","url":"/rsvp"}, {"name":"Registry","url":"/registry"}, {"name":"Guestbook","url":"/guestbook"}, {"name":"Program","url":"/program"}, {"name":"Photos","url":"/photos"}],
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
    "tour": True,
	"types": ['Asian', 'Barbecue', 'Breakfast', 'Brewpub', 'Burmese', 'Caribbean', 'Chinese', 'Ethiopian', 'Greek', 'Indian', 'Indian ', 'Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Moroccan', 'Persian', 'Picnic', 'Pizza', 'Seafood', 'Shave Ice', 'Thai', 'Vietnamese']
    }
    # Get number of days until the big day
    template_values['action']=ctx.request.get('action') 
    template_values['days']=int((datetime(2017,4,16,20,0)-datetime.now()).total_seconds()/86400+0.5)
    template_values['hours']=int((datetime(2017,4,16,20,0)-datetime.now()).total_seconds()/3600)
    template_values['nickname']=ctx.session_store.get_session().get('nickname') 
    if users.get_current_user() and names.get(users.get_current_user().nickname()):
        template_values['nickname'] = names[users.get_current_user().nickname()]
        ctx.session['nickname'] = template_values['nickname']
    if template_values.get('nickname'):
        template_values['nickname']=template_values['nickname'].title()
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
        rsvp_count=get_RSVP_count(rsvp_list)
        template_values['rsvpcount']=rsvp_count
        template_values['guestcount'] = rsvp_count.get("HI").get("count",0)
        if template_values["nickname"] in names.keys() or template_values["nickname"] in names.values() :
            template_values["weddingparty"]="Yes"
        template = jinja_environment.get_template('ceremony.html')
        self.response.out.write(template.render(template_values))

def login_key(guestbookName=app_name):
    """Constructs a Datastore key for a Login entity with guestbookName."""
    return ndb.Key('Login', guestbookName)

class Event(ndb.Model):
    event_id = ndb.IntegerProperty(required=True)
    pick_no = ndb.IntegerProperty(indexed=False)
    event_name = ndb.StringProperty()
    event_json = ndb.JsonProperty()
    
class Login(ndb.Model):
    """Models an individual Login entry."""
    nickname = ndb.StringProperty(indexed=False)
    login_date = ndb.DateTimeProperty(auto_now_add=True)

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.StringProperty()
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
    carrier = ndb.StringProperty(indexed=False)
    contactMethod = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    willAttendCA= ndb.TextProperty(indexed=False)
    willAttendWI= ndb.TextProperty(indexed=False)
    request = ndb.JsonProperty()
   
class Response(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('rsvp.html')
        template_values = globalVals(self) 
        rsvp_list = get_RSVP_list()
        template_values['rsvp_list']=rsvp_list
        rsvp_count=get_RSVP_count(rsvp_list)
        template_values['rsvpcount']=rsvp_count
        template_values['guestcount']=rsvp_count.get("HI").get("count",0)
        for rsvp in rsvp_list:
            if rsvp.nickname in (template_values['nickname'], self.request.get('nickname')):
                template_values['rsvp'] = rsvp
                if not rsvp.request:
                    rsvp.request={}
                template_values.update(rsvp.request)
                reply = max(rsvp.willAttend,rsvp.willAttendCA,rsvp.willAttendWI)
                template_values['msg'] = template_values.get(reply,"")
                template_values['emoticon'] = template_values['emoti'].get(reply,"")
        if template_values["nickname"] in names.keys() or template_values["nickname"] in names.values() :
            template_values["weddingparty"]="Yes"
        self.response.write(template.render(template_values))

    def post(self):
        globalvals=globalVals(self)
        guestbookName = self.request.get('guestbookName', app_name)
        rsvp_key = self.request.get('nickname')
        if not rsvp_key or rsvp_key in ('None','Guest'):
            rsvp_key = self.request.get('name')
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
        rsvp.attendees = int(self.request.get('attendees',1))
        rsvp.note = self.request.get('note')
        rsvp.contactMethod = self.request.get('contactMethod')
        rsvp.carrier = self.request.get('carrier')
        rsvp.request = {}
        for arg in self.request.arguments():
            if self.request.get(arg):
                rsvp.request[arg]=self.request.get(arg)
        rsvp.put()
        memcache.delete("RSVP")
        # Add a Greeting if the note is filled in 
        if rsvp.note:
            greeting = Greeting(parent=guestbook_key(guestbookName))
            greeting.author = rsvp_key
            greeting.content = rsvp.note
            greeting.put() 
            memcache.delete("greetings")            
        if rsvp.contactMethod=='text' and rsvp.carrier and rsvp.willAttend =='yes':
            message = mail.EmailMessage(sender=globalvals['sender'], subject=globalvals['subject'])
            message.to = rsvp.phone + "@" + rsvp.carrier
            message.bcc = "steve@susyandsteve.com"
            message.body = "Hi " + rsvp.nickname  + ". Thank you for attending our wedding. See you there! :)"
            message.send()
        elif rsvp.contactMethod=='text' and rsvp.carrier and (rsvp.willAttendCA =='yes' or rsvp.willAttendWI =='yes'):
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
        else:
            message = mail.EmailMessage(sender=globalvals['sender'], subject="New Wedding RSVP from "+rsvp.name)
            message.to = "us@susyandsteve.com"
            message.html = rsvp.nickname + " responded " + rsvp.willAttend+globalvals['emoti'][rsvp.willAttend] + "<p>Susy & Steve<br>http://susyandsteve.com"
            message.send()        
        self.redirect('/login?nickname='+rsvp_key)

class LogMeInOrOut(BaseHandler):
    def get(self):
        if self.request.url.endswith("logout") and self.session.get("nickname"):
            del self.session["nickname"]
            nickname=None
        else:
            nickname = self.request.get('nickname')
            if not nickname or nickname in ('Guest','None','undefined'):
                nickname = self.session.get('nickname')
        if not nickname:
            template = jinja_environment.get_template('index.html')
            template_values = globalVals(self) 
            template_values['request']=self.request
            self.response.write(template.render(template_values))
        else:
            nickname=nickname.title()
            guestbookName = self.request.get('guestbookName', app_name)
            login = Login(parent=login_key(guestbookName), id=nickname)
            login.nickname = nickname
            self.session['nickname'] = nickname
            login.put()
            self.redirect('/rsvp')
            

    def post(self):
        # Login the user and save in the session
        nickname = self.request.get('nickname').lower()
        # If input is gmail (xxx@gmail.com), redirect to Google login page
        if nickname.find('@gmail.com')>0:
            self.redirect(self.request.get('url'))
        if nickname.title() != 'Guest':
            guestbookName = self.request.get('guestbookName', app_name)
            login = Login(parent=login_key(guestbookName), id=nickname)
            login.nickname = nickname
            if users.get_current_user():
                login.nickname = users.get_current_user().nickname()
            self.session['nickname'] = nickname
            login.put()
        self.redirect('/')

class Ceremony(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('ceremony.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))

def guestbook_key(guestbookName=app_name):
    """Constructs a Datastore key for a Guestbook entity with guestbookName."""
    return ndb.Key('Guestbook', guestbookName)

# Function to tag invalid greetings
def valid_greeting(author,content,filter):
    filters=["href","http"]
    is_valid=True
    if not author or not author[0].isupper() or author in ('None','Guest'):
        is_valid=False
    elif not content:
        is_valid=False
    elif any(filter in content for filter in filters):
        is_valid=False
    return is_valid

def delete_greetings(filter):
    greetings_query = Greeting.query(ancestor=guestbook_key(app_name)).order(-Greeting.date)
    greetings = greetings_query.fetch(1000)
    for greeting in greetings:
        if not valid_greeting(greeting.author,greeting.content):
            greeting.key.delete()
    memcache.delete("greetings")            
    
def get_greetings():
    greetings=memcache.get("greetings")
    if not greetings:
        greetings_query = Greeting.query(ancestor=guestbook_key(app_name)).order(Greeting.date)
        greetings = greetings_query.fetch(50)
        memcache.add("greetings",greetings)
    return greetings
    
def getEvent(event_id):
    event=Event.get_by_id(int(event_id))
    if event:
        event_data=event.event_json
    else:
        event_data=default_event(event_id)
    return event_data  

def getEvents():
    events = memcache.get('events')    
    if not events:
        events=[{"event_id": event.event_id, "event_name": event.event_name } for event in Event.query().order(-Event.event_id).fetch(10)]
        memcache.add("events",events)
    return events  
    
def getResults(event_id):
    results=getEvent(event_id).get('results')
    results_key='results'+str(event_id)
    resultstr = memcache.get(results_key)
    if resultstr:
        results=json.loads(resultstr)
    else:		
        try:
            results=get_results(int(event_id))
            resultstr=str(json.dumps(results))
            memcache.add(results_key,resultstr,240)
        except:
            memcache.delete(results_key)    
    return results

def getRestaurants():
    reststr = memcache.get("restaurants")
    if reststr:
        restaurants=json.loads(reststr)
    else:		
        try:
            restaurants=fetch_restaurants()
            reststr=str(json.dumps(restaurants))
            memcache.add("restaurants",reststr,240)
        except:
            memcache.delete("restaurants")    
    return restaurants

def setRestaurants(rest_type):
    try:
        restaurants=fetch_restaurants(rest_type)
        reststr=str(json.dumps(restaurants))
        memcache.add("restaurants",reststr,60)
    except:
        memcache.delete("restaurants")    
    return restaurants
	

def updateEvent(event_data):
    event_id = int(event_data["event_id"])
    event=Event(id=event_id,event_id=event_id,event_name=event_data["event_name"],pick_no=event_data["pick_no"],event_json=event_data)
    event.put()
    memcache.delete("event")
    memcache.add("event",str(json.dumps(event_data)))

def updateResults(event_id,results):
    event_data=getEvent(event_id)
    event_data['results']=results
    updateEvent(event_data)

class EventHandler(BaseHandler):
    def get(self):     
        event_id = int(self.request.get('event_id',currentEvent()))
        output=self.request.get('output')
        if "results" in self.request.url:
            results=getResults(event_id)
            if results:
                updateResults(event_id,results)
                template_values = { 'results': getResults(event_id) }
                template = jinja_environment.get_template('results.html')
                self.response.out.write(template.render(template_values))
        elif "events" in self.request.url:
            events=memcache.get('events')
            if not events:
                events=fetch_events()
                memcache.add("events",events)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write({"events":events})
        else:
            event = getEvent(event_id)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(event))
            
    def post(self):     
        event_data = self.request.get('event_data')
        event_json = json.loads(event_data)
        updateEvent(event_json)
        event_id = str(event_json["event_id"])
        self.redirect('/golfevent?event_id=' +event_id) 

class MailHandler(BaseHandler):
    def get(self):     
        event_id = int(self.request.get('event_id',currentEvent()))
        event = getEvent(event_id)
        results = getResults(event_id)
        if event and results:
            message = mail.EmailMessage(sender='admin@susyandsteve.appspotmail.com', subject=event["event_name"]+" ("+results["event"]["Status"]+")")
            message.to = "sholtebeck@gmail.com"
            message.cc = "ingrahas@gmail.com"
            result = urllib2.urlopen(results_url)
            message.html=result.read()
            message.send()
                   
class GolfPicks(BaseHandler):
    def get(self):     
        event_id = int(self.request.get('event_id',currentEvent()))
        event = getEvent(event_id)
        pick_no = event["pick_no"]
        picknum = pick_ord[pick_no]
        # get next player
        if picknum != "Done":
            event["next"]=event["pickers"][0] if mypicks.count(pick_no)>0 else event["pickers"][1]
        else:
            event["next"]="Done"
        # check results
        event["results_url"]=results_url+"?event_id="+str(event_id)
        if users.get_current_user():
            user = names[users.get_current_user().nickname()]
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            user = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
     
        template_values = {
            'results': current_ym() - event_id,
            'event': event,
			'events': getEvents(),
            'pick_no': pick_no,
            'picknum': picknum,
            'url': url,
            'url_linktext': url_linktext,
            'user': user
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        event_id=self.request.get('event_id')
        event=getEvent(event_id)     
        who= self.request.get('who')
        pick_no = int(self.request.get('pick_no'))
        player = self.request.get('player')
        # update event (add to picks, remove from field)
        event = getEvent(event_id)
        if player in event["picks"]["Available"]:
            event["picks"]["Available"].remove(player)
            event["picks"]["Picked"].append(player)
            event["picks"][who].append(player)
            event["lastpick"]=who+" picked "+player
            event["pick_no"]+=1
            updateEvent(event)
        self.redirect('/golfpicks?event_id=' +event_id) 
    
class Guestbook(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('guestbook.html')
        template_values = globalVals(self) 
        guestbookName = self.request.get('guestbookName',app_name)
        greetings = get_greetings()
        template_values = globalVals(self)
        template_values['greetings'] =  greetings
        template_values['guestbookName'] = urllib.quote_plus(guestbookName)
        template_values['postmessage']=True
        self.response.write(template.render(template_values)) 
        
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        author=self.request.get('author')
        content = self.request.get('content')
        guestbookName = self.request.get('guestbookName', app_name)      
        if valid_greeting(author,content,'href'):
            memcache.delete("greetings")
            greeting = Greeting(parent=guestbook_key(guestbookName))
            greeting.author = author
            greeting.content = content
            greeting.put()
        elif author=='delete':
            delete_greetings(content)   
        queryParams = {'guestbookName': guestbookName}
        self.redirect('/guestbook?guestbookName=nopost')

class Photos(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('photos.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))       

class PlayersHandler(BaseHandler):   
    def get(self):
        event_id = self.request.get('event_id')
        if event_id:
            event = getEvent(event_id)
        else:
            event = getEvent(currentEvent())
        output_format = self.request.get('output')
        if not output_format:
            output_format='html'
        players=getPlayers()
        self.response.headers['Content-Type'] = 'application/json'
        template_values = { 'event': {"name":event.get('event_name') }, "players": players }
        self.response.write(json.dumps(template_values))
		
		
class Registry(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('registry.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))       

class Restaurants(BaseHandler):    
    def get(self):
        output_format = self.request.get('output')
        if not output_format:
            output_format='html'
        if output_format=='json':
            restaurants = getRestaurants()
            types=sorted(list(set([rest.get('Type').strip() for rest in restaurants])))
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps({"restaurants":restaurants, "types":types }))
        elif output_format=='html':
            self.redirect("/app/restaurants.html") 
			
    def post(self):
        rest_type = self.request.get('rest_type') 
        if rest_type:
            setRestaurants(rest_type)		
        self.redirect("/app/restaurants.html")      
        
		
class Guests(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('guests.html')
        template_values = globalVals(self)
        attending=self.request.get('attending')          
        if not template_values['nickname']:
            self.redirect(template_values['url'])
        else:
            rsvp_list = get_RSVP_list()
            template_values['rsvp_list']=rsvp_list
            rsvp_count=get_RSVP_count(rsvp_list)
            template_values['rsvpcount']=rsvp_count
            guest_list = []
            for rsvp in rsvp_list:
                if (attending in ("HI","yes") and rsvp.willAttend=="yes") or (attending=="CA" and rsvp.willAttendCA=="yes") or (attending=="WI" and rsvp.willAttendWI=="yes") or (not attending):
                    rsvp_dict={"Name":rsvp.name, "Address":rsvp.address, "City":rsvp.city,"State":rsvp.state,"Zip":rsvp.zip,"Email":rsvp.email,"Phone":rsvp.phone, "WillAttend":rsvp.willAttend,
                    "WillAttendCA":rsvp.willAttendCA, "WillAttendWI":rsvp.willAttendWI, "Attendees":rsvp.attendees,"Other":''}
                    for key in template_values['extras']:
                        if rsvp.request and rsvp.request.get(key):
                            rsvp_dict['Other']+=' '+key.title()
                            if rsvp.request[key]!='on':
                                rsvp_dict['Other']+=':'+str(rsvp.request[key])+'<br>'
                    guest_list.append(rsvp_dict)
            template_values['guest_list'] =  guest_list
            template_values['title'] = "Guests for " + template_values['title']
            template_values['guestcount'] = 0
            self.response.write(template.render(template_values))
			
class Program(BaseHandler):
    def get(self):
        self.redirect("/app/WeddingProgram.pdf")      

class Travel(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('travel.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))        
             
class WeddingBlog(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('wedlog.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))        

class WeddingList(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('wedlist.html')
        template_values = globalVals(self) 
        rsvp_list = get_RSVP_list()
        template_values['rsvp_list']=rsvp_list
        self.response.write(template.render(template_values))           
        
class WeddingTour(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('weddingtour.html')
        template_values = globalVals(self) 
        self.response.write(template.render(template_values))
        
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/ceremony',Ceremony),
    ('/golfevent',EventHandler),
    ('/golfevents',EventHandler),
    ('/results',EventHandler),
    ('/golfpicks',GolfPicks),
    ('/guests',Guests),
    ('/guestbook',Guestbook),
    ('/program', Program), 
    ('/players', PlayersHandler), 
    ('/photos', Photos),
    ('/registry', Registry),
    ('/restaurants', Restaurants),
    ('/rsvp', Response),
    ('/login', LogMeInOrOut),
    ('/logout', LogMeInOrOut),
    ('/mail', MailHandler),
    ('/travel',Travel), 
    ('/wedlist',WeddingList), 
    ('/wedlog',WeddingBlog), 
    ('/weddingtour',WeddingTour),
], config=config,debug=True)

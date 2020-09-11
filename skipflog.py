#module with skipflog functions
import csv,json,sys,urllib2
import datetime as dt
from time import gmtime, strftime


# Misc properties
cache={}
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','ingrahas':'Susy'}
numbers={'Steve':'5103005644@vtext.com','Susy':'8082719138@vtext.com'}
pick_ord = ["None", "First","First","Second","Second","Third","Third","Fourth","Fourth","Fifth","Fifth", "Sixth","Sixth","Seventh","Seventh","Eighth","Eighth","Ninth","Ninth","Tenth","Tenth","Alt.","Alt.","Done"]
event_url="https://docs.google.com/spreadsheet/pub?key=0Ahf3eANitEpndGhpVXdTM1AzclJCRW9KbnRWUzJ1M2c&single=true&gid=1&output=html&widget=true"
events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A2%3AE21&output=csv"
players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=B2%3AB155&output=csv"
results_tab="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=2&output=html"
ranking_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=3&output=html"
restaurants_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vQNXUwwyo5UsN4d50Y2N5678rkpWOFn8UFczKt9F644d0BuWTiSZPMz86a2yCkqyCbLIg5WiEDWFofS/pub?gid=0&single=true&output=csv"
rankings_url="http://knarflog.appspot.com/ranking"
result_url="http://knarflog.appspot.com/results"
results_url="http://susyandsteve.appspot.com/results"
players_api="http://knarflog.appspot.com/api/players"
leaderboard_url="http://sports.yahoo.com/golf/pga/leaderboard"
mapsearch="https://www.google.com/maps/search/?api=1&query="
skip_user="skipfloguser"
skip_picks={}
skip_pickers=["Susy","Steve"]
#skip_points=[0, 100, 60, 40, 35, 30, 25, 20, 15, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2]
skip_points=[0, 100, 60, 40, 30, 24, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9.5, 9, 8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,4,3.5,3.5,3,3,2.5,2.5,2,2,2,1.5,1.5]
res_keys=['POS', 'Name', 'PLAYER', 'TO PAR', 'TODAY', 'THRU', 'R1', 'R2', 'R3', 'R4', 'Scores', 'Points','Rank','Total','TOT']

# Misc urls
espn_url="http://www.espn.com/golf/leaderboard"
feed_url='https://spreadsheets.google.com/feeds'
golfchannel_url="http://www.golfchannel.com/tours/usga/2014/us-open/"
invite_url='http://www.masters.com/en_US/xml/gen/players/invitees_2017.xml'
owg_url="http://www.owgr.com/en/Events/EventResult.aspx?eventid=5520"
pga_url="http://www.pga.com/news/golf-leaderboard/pga-tour-leaderboard"
pgatour_url="http://www.pgatour.com/leaderboard.html"
picks_csv = "picks.csv"
picks_url = "http://susyandsteve.appspot.com/golfevent?event_id="
players_api = "http://knarflog.appspot.com/api/players"
rankings_api = 'https://us-west2-skipflog.cloudfunctions.net/getRankings'
results_api="https://us-west2-skipflog.cloudfunctions.net/getResults"
owg_ranking_url="http://www.owgr.com/ranking"
yahoo_base_url="http://sports.yahoo.com"
yahoo_url=yahoo_base_url+"/golf/pga/leaderboard"
debug=False

# get the current Event
def currentEvent():
    now=dt.datetime.now()
    event_month=min(max(now.month,4),11)
    event_current=100*(now.year-2000)+event_month
    return event_current

# get current week and year
def current_month():
    this_month=strftime("%m",gmtime())
    return int(this_month) 

def current_week():
    this_week=strftime("%U",gmtime())
    return int(this_week)-1 

def current_year():
    this_year=strftime("%Y",gmtime())
    return int(this_year) 

def current_ym():
    this_ym=strftime("%y%m",gmtime())
    return int(this_ym) 

def current_time():
    right_now=strftime("%H%M",gmtime())
    return str(right_now) 
    
# determine the cut rank for the various majors (Masters=50, US=60, Open,PGA=70)
def cut_rank():
    this_month=current_month()
    if this_month == 4:
        return 50
    elif this_month == 6:
        return 60
    else:
        return 70
     
# debug values
def debug_values(number, string):
    if debug:
        print (number, string)

# Get the value for a string
def get_value(string):
    string=string.replace(',','').replace('-','0')
    try:
        value=round(float(string),2)
    except:
        value=0.0
    return value
    
# Handler for string values to ASCII or integer
def xstr(string):
    if string is None:
        return None 
    elif type(string)!=type(""):
        return string
    elif string.isdigit():
        return int(string)
    else:
        return str(string.encode('ascii','ignore').strip())

# Function to get_points for a Position
def get_rank(position):
    if not position.replace('T','').isdigit():
        return 99
    else:
        rank = int(position.replace('T',''))
        return rank

def get_points(rank):
    if rank < len(skip_points):
        return skip_points[rank]
    elif rank <= cut_rank():
        return 1
    else:
        return 0

def fetchEvents():
    if cache.get("events"):
        return cache["events"]
    events_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=0&range=A1%3AE41&output=csv"
    result = urllib2.urlopen(events_url)
    reader = csv.DictReader(result)
    event_list=[]
    for row in reader:
        row["first"]=row["first"].replace("Mark","Susy")
        event_list.append(row)
    cache["events"]=event_list
    return event_list

def get_pickers(first):
    pickers=[sp for sp in skip_pickers if sp==first]+[sp for sp in skip_pickers if sp!=first]
    return [{"name":p,"number": numbers.get(p), "picks":[],"points":0} for p in pickers]

# Get a default event dictionary
def default_event(event_id=currentEvent()):
    event=[e for e in fetchEvents()][0]
    event["event_id"]=int(event['ID'])
    event["event_year"]=int(event['Name'][:4])
    event["event_name"]=event['Name']
    event["next"]=event["first"]
    event["nextpick"]=event["next"]+"'s First Pick"
    event["pickers"]=get_pickers(event["first"])
    event["players"]=fetchPlayers()
    event["pick_no"]=1 
    return event

# Get the rankings from the page
def get_rankings(size):
    rankings=json_results(rankings_api)
    return rankings.get("players")

# Get the picks for an event
def get_picks(event_id):
    picks={}
    pickdict=json_results(picks_url+str(event_id))
    if pickdict.get("picks"):
        for picker in skip_pickers:
            picklist=[str(pick) for pick in pickdict["picks"][picker][:10]]
            picks[picker]={'Name':picker,'Count':len(picklist),'Picks':picklist,'Points':0}
            for pick in picklist:
                picks[str(pick)]=picker
    elif pickdict.get("pickers"):
        for picker in pickdict["pickers"]:
            pickname=picker["name"]
            picklist=picker["picks"][:10]
            picks[pickname]={'Name':pickname,'Count':len(picklist),'Picks':picklist,'Points':0}
            for pick in picklist:
                picks[str(pick)]=picker
    return picks

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

def search_query(restaurant):
    if restaurant.get("Name"):
        query=restaurant["Name"].lower().replace(" ","+")
    elif restaurant.get("Address"):
        query=restaurant["Address"].lower().replace(" ","+")
    return query
    
def fetch_restaurants():
    result = urllib2.urlopen(restaurants_url)
    reader = csv.DictReader(result)
    rest_list=[row for row in reader]
    for r in range(len(rest_list)):
        rest_list[r]["Maplink"]=mapsearch+search_query(rest_list[r])
    return rest_list
  
# Get the list of players from a spreadsheet (players tab)
def fetchPlayers():
    if cache.get("players"):
        return cache["players"]
    cache["players"]=players=json_results(players_api).get("players")
    return players      
        
# Get the list of players
def get_players(playlist):
    current_rank=1
    players=[]
    for player in playlist:
        if player.get('Picker'):
            players.append([current_rank,player['Name'],player['Avg'],player['Week'],player['Rank'],player['Points'],player['Picker']])
            current_rank+=1
    return players
 
def get_results(event_id):
    picks=get_picks(event_id)
    for name in skip_pickers:
       picks[name]["Count"]=0
       picks[name]["Points"]=0
    results=json_results(results_api)
    tie={"Points":100,"Players":[]}
    for res in results["players"]:
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
            picks[picker]["Count"]+=1
            picks[picker]["Points"]+=1
    results['players']=[p for p in results['players'] if p.get("Picker") or p.get("Points")>20]
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    results['pickers'][0]['Rank']=1
    results['pickers'][1]['Rank']=2
    return results
    
def next_pick(picknames,pick_no):
    picknum=pick_ord[pick_no%len(pick_ord)]
    if picknum == "Done":
        return ("Done", "We're Done")
    elif pick_no in mypicks:
        return (picknames[0],picknum)
    else:
        return (picknames[1],picknum)

# Update an event with a picked player. Passing an event dict and an "X picked Y message"
#  Verify that picker X is next and player Y is available (not picked yet)
def pick_player(event, player):
    new_event=event.copy()
    picker=event["next"]
    picknames=[n["name"] for n in event["pickers"]]
    playnames=[p["name"]+("z"*p["picked"]) for p in event["players"]]
    if picker in picknames and player in playnames:
        p=picknames.index(picker)
        q=playnames.index(player)
        new_event["pickers"][p]["picks"].append(player)
        new_event["players"][q]["picked"]=1
        new_event["pick_no"]=event["pick_no"]+1
        if event.get("lastpick") and event["lastpick"].startswith(picker):
            new_event["lastpick"]=event["lastpick"]+" and "+player
        else:
            new_event["lastpick"]=picker+" picked "+player
        picknext,picknum=next_pick(picknames,new_event["pick_no"])
        new_event["next"]=picknext
        if picknext:
            new_event["nextpick"]=picknext+"'s "+picknum+" Pick"
        else:
            new_event["nextpick"]=picknum
    return new_event
    

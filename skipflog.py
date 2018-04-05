#module with skipflog functions
import csv,json,sys,urllib2
import datetime as dt
from time import gmtime, strftime
# External modules (gspread, bs4)
import sys
sys.path[0:0] = ['libs']
import gspread
from bs4 import BeautifulSoup
from oauth2client.client import SignedJwtAssertionCredentials

# Misc properties
br="</br>"
events={ 4:'Masters',6:'US Open', 7:'Open Championship', 8:'PGA Championship'}
mypicks = [1,4,5,8,9,12,13,16,17,20,22]
yrpicks = [2,3,6,7,10,11,14,15,18,19,21]
names={'sholtebeck':'Steve','ingrahas':'Susy'}
numbers={'Steve':'5103005644@vtext.com','Susy':'6149848290@vmobl.com'}
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
rankings_api = "http://knarflog.appspot.com/api/rankings/"
results_api = "http://knarflog.appspot.com/api/results/"
owg_ranking_url="http://www.owgr.com/ranking"
yahoo_base_url="http://sports.yahoo.com"
yahoo_url=yahoo_base_url+"/golf/pga/leaderboard"
debug=False

# get the current Event
def currentEvent():
    now=dt.datetime.now()
    event_month=min(max(now.month,4),8)
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
        print number, string

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
        
# Get a default event dictionary
def default_event(event_id=currentEvent()):
    event={"event_id":event_id }
    event["event_year"]=2000+(int(event_id)/100)
    event["event_name"]=str(event["event_year"])+" "+events.get(int(event_id)%100)
    event["pickers"]=skip_pickers
    event["next"]=skip_pickers[0]
    event["picks"]={"Picked":[],"Available":[] }
    for picker in skip_pickers:
        event["picks"][picker]=[]
    event["picks"]["Available"]=fetch_players(espn_url)
    event["pick_no"]=1  
    return event

# Get the rankings from the page
def get_rankings(size):
    ranking_url="http://www.owgr.com/ranking?pageSize="+str(size)
    soup=soup_results(ranking_url)
    rankings=[]
    rank=1
    for row in soup.findAll('tr'):
        name = row.find('a')
        if name:
            points = float(row.findAll('td')[6].string)
            player={"rank":rank, "name":str(name.string), "points":points }
            rankings.append(player)
            rank+=1
    return rankings

# Get the picks for an event
def get_picks(event_id):
    picks={}
    pickdict=json_results(picks_url+str(event_id))
    if pickdict['picks']:
        for picker in skip_pickers:
            picklist=[str(pick) for pick in pickdict["picks"][picker][:10]]
            picks[picker]={'Name':picker,'Count':len(picklist),'Picks':picklist,'Points':0}
            for pick in picklist:
                picks[str(pick)]=picker
    return picks

def open_worksheet(spread,work):
    json_key = json.load(open('skipflog.json'))
    scope = [feed_url]
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    gc = gspread.authorize(credentials)
    spreadsheet=gc.open(spread)
    worksheet=spreadsheet.worksheet(work)
    return worksheet

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup

def fetch_headers(soup):
    if not soup:
        return None
    headers={}
    headers['Year']=current_year()
#   event_name = soup.find('h4',{'class': "yspTitleBar"})
#   event_name = soup.find('h1',{'class': "tourney-name"})
    event_name = soup.find('title')
    if event_name and event_name.string:
        event_string=str(event_name.string.replace(u'\xa0',u''))
        headers['Name']=event_string[:event_string.index(' Golf')]
    last_update = soup.find('span',{'class': "ten"})
    if last_update:
        headers['Last Update']= str(last_update.string[-13:])
    else:
        headers['Last Update']= current_time()
    thead=soup.find('thead')
    headers['Status']=str(soup.find("span",{"class":"tournament-status"}).string)
    if headers['Status'].startswith("Round "):
        headers['Round']=headers['Status'][6]
    headers['Round']=dt.datetime.today().weekday()-2
    table=soup.findAll("table")[-1]
    headers['Columns']=[str(th.string) for th in table.findAll('th')]
    return headers

def fetch_players(url):
    players=[]
    soup=soup_results(url)
    for row in soup.findAll('tr'):
        name = row.find('a')
        if name:
            player_name=str(name.string)
            players.append(player_name)
    players.sort()
    return players

def fetch_rankings(row):
    name = row.find('a')
    cols = row.findAll('td')
    player={}
    if name and len(cols)>=10:
        player_name=str(name.string)
        player={'Rank': int(cols[0].text), 'Name': player_name }
        player['Country']= str(cols[3].img.get('title'))
        player['Average']=float(cols[5].text)
        player['Total']=float(cols[6].text)
        player['Events']=int(cols[7].text)
        player['Points']=float(cols[9].text) 
    return player
       
def fetch_results(row, columns):
    results={}
    player=row.find('a')
    if player:
        results['Name']=str(player.string)
        debug_values('Name',results['Name'])
#       results['Link']=yahoo_base_url+str(player.get('href'))
#       debug_values('Link',results['Link'])
        values=[val.string for val in row.findAll('td')]
        for col,val in zip(columns,values):
            if col not in ("None",None):
                results[col]=str(val)
        # Change CUT to MC
        if results.get("TO PAR")=="CUT" or results.get("THRU")=="CUT" :
            results["POS"]="MC"
            results["TO PAR"]="MC"
        # Get Rank and Points
        results['Rank']=get_rank(results.get('POS','99'))
        results['Points']=get_points(results['Rank'])
        # Get Scores
        scores=[]
        for round in ("R1","R2","R3","R4"):
            if results.get(round) and results.get(round) not in ("--"):
                scores.append(results.get(round))
                results["Today"]=results[round]
        results['Scores']="-".join(scores)
        # Get Today
        if not results.get('THRU'):
            results['THRU']='-'
        elif results.get('THRU')=='F':
            results['Today']+='('+results['TODAY']+')'
        elif results.get('THRU').isdigit():
            results['Today']='('+results['TODAY']+') thru '+results['THRU']
            results['Total']='('+results['TO PAR']+') thru '+results['THRU']
        elif results['THRU'][-2:] in ('AM','PM'):
            results['Time']='@ '+results['THRU']
        elif results['THRU'] in ('MC','CUT','WD','DQ'):
            results['Rank']=results['THRU']
            results['Today']=results['THRU']
        # Get Total
        if results.get('TOT') not in (None,"--"):
            results['Total']=results['TOT']+'('+results['TO PAR']+')'
        # Validate/Filter results
        for key in results.keys():
            if key not in res_keys or results[key] in (None,"None","-","--"):
                del results[key]
            else:
                results[key]=xstr(results[key])
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
	
def fetch_scores(url):
    scores=[[],[], 0,0]
    page=soup_results(url)
    rows=fetch_rows(page)
    cols=[]
    if len(rows)>4:
        cols=rows[3].findAll('td')
    holenum=0
    for col in cols:
        if col.string.isdigit():
            score=int(col.string)
            if score < 20:
                debug_values(holenum, score)
                if holenum<10:
                    scores[0].append(str(score))
                    scores[2]+=score
                else:
                    scores[1].append(str(score))
                    scores[3]+=score
            else:
                holenum-=1 
        holenum+=1
    scores.append(scores[2]+scores[3])
    return scores       

def fetch_tables(url):
    page=soup_results(url)
    tables=page.findAll('table')
    results=''
    for table in tables:
        results=results+str(table)
        results=results+"<p>"
    return results[:-3]

# fetch all table rows
def fetch_rows(page):
#   return page.find('table').findAll('tr')    
    return page.findAll('tr')    

# fetch the url for an event
def fetch_url(event_id):
    url={
	1604: 'http://www.espn.com/golf/leaderboard?tournamentId=2493', 
	1606: 'http://www.espn.com/golf/leaderboard?tournamentId=2501', 
	1607: 'http://www.espn.com/golf/leaderboard?tournamentId=2505', 
	1608: 'http://www.espn.com/golf/leaderboard?tournamentId=2507',
	1704: 'http://www.espn.com/golf/leaderboard?tournamentId=2700', 
	1706: 'http://www.espn.com/golf/leaderboard?tournamentId=3066', 
	1707: 'http://www.espn.com/golf/leaderboard?tournamentId=2710', 
	1708: 'http://www.espn.com/golf/leaderboard?tournamentId=2712',
	1804: 'http://www.espn.com/golf/leaderboard'}
    if url.get(event_id):
        return url[event_id]
    else:
        return None

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
    event_url=fetch_url(event_id)
    page=soup_results(event_url)
    results={}
    tie={"Points":100,"Players":[]}
    results['event']=fetch_headers(page)
    results['players']=[]
    rows=fetch_rows(page)
    for row in rows:
        res=fetch_results(row, results.get('event').get('Columns'))
        if res.get('Name') in picks.keys():
            picker=xstr(picks[res['Name']])
            res['Picker']=picker
        if res.get('Points')>=9:
            if res["Points"]!=tie.get("Points"):
                if len(tie["Players"])>1:
                   tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
                   for p in tie["Players"]:
                        results["players"][p]["Points"]=tie["Points"]
                tie={"Players": [len(results['players'])], "Points":res["Points"], "POS":res["POS"]}
            else:
                tie["Players"].append(len(results['players']))
        if res.get('Picker') or res.get('Points')>=9:
            results['players'].append(res)
    if len(tie["Players"])>1:
        tie["Points"]=float(sum([skip_points[p+1] for p in tie["Players"]]))/len(tie["Players"])
        for p in tie["Players"]:
            results["players"][p]["Points"]=tie["Points"]    
    for picker in skip_pickers:
        picks[picker]["Count"]=len([player for player in results.get("players") if player.get("Picker")==picker])
        picks[picker]["Points"]=sum([player["Points"] for player in results.get("players") if player.get("Picker")==picker])
    results['pickers']=[picks[key] for key in picks.keys() if key in skip_pickers]
    if results['pickers'][1]['Points']>results['pickers'][0]['Points']:
        results['pickers'].reverse()
    results['pickers'][0]['Rank']=1
    results['pickers'][1]['Rank']=2
    return results
    
# Update the picks to the Players tab in Majors spreadsheet
def pick_players(picklist):
    try:
        players=json_results(players_api)
        worksheet=open_worksheet('Majors','Players')
        for player in players['players']:
            if player['name'] in picklist:
                worksheet.update_cell(player["rownum"], 6, 1)
    except:
        pass

def pick_player(name):
    players=json_results(players_api)
    worksheet=open_worksheet('Majors','Players')
    for player in players['players']:
        if player['name']==name:
            worksheet.update_cell(player["rownum"], 6, 1)
    
# Post the players to the Players tab in Majors spreadsheet
def post_players():
    current_csv='https://docs.google.com/spreadsheets/d/1v3Jg4w-ZvbMDMEoOQrwJ_2kRwSiPO1PzgtwqO08pMeU/pub?single=true&gid=0&output=csv'
    result = urllib2.urlopen(current_csv)
    rows=[row for row in csv.reader(result)]
    names=[name[1] for name in rows[3:]]
    names.sort()
    rankings=get_rankings(999)
    rank_names=[rank['name'] for rank in rankings]
    worksheet=open_worksheet('Majors','Players')
    current_row=2
    for name in names:
        if name in rank_names:
            player=rankings[rank_names.index(name)]
            worksheet.update_cell(current_row, 1, player['rank'])
            worksheet.update_cell(current_row, 2, player['name'])
            worksheet.update_cell(current_row, 3, player['points'])
        else:
            worksheet.update_cell(current_row, 1, 999)
            worksheet.update_cell(current_row, 2, name)
            worksheet.update_cell(current_row, 3, 0.0)
        current_row += 1
    return True

# Post the rankings to the "Rankings" tab
def post_rankings():
    this_week=str((current_year()-2000)*100+current_week())
    results=json_results(rankings_api+this_week)
    worksheet=open_worksheet('Majors','Rankings')
    #get date and week number from header
    results_date=results['headers']['date']
    results_week=int(results['headers']['Week'])
    worksheet_week=int(worksheet.acell('D1').value)
    # check if update required
    if (results_week==worksheet_week):
        return False
    else:
        worksheet.update_cell(1, 4, results_week)
        worksheet.update_cell(1, 2, results_date)
    #get all table rows from the page
    players=get_players(results['players'])
    players.sort(key=lambda player:player[5], reverse=True)
    current_row=3
    pickvals={}
    for picker in skip_pickers:
        pickvals[picker]={'count':0,'total':0.0,'points':0.0 }
    for player in players:
        picker = player[6]
        if (pickvals[picker]['count']<15):
            player[0]=current_row-2
            cell_values = worksheet.range('A'+str(current_row)+':G'+str(current_row))
            for col,cell in zip(player,cell_values):
                cell.value=col
            worksheet.update_cells(cell_values)
            pickvals[picker]['total']+=float(player[3])
            pickvals[picker]['points']+=player[5]
            pickvals[picker]['count']+=1
            current_row += 1
    # update totals
    if pickvals[skip_pickers[1]]['points']>pickvals[skip_pickers[0]]['points']:
        skip_pickers.reverse()
    current_row+=1
    for picker in skip_pickers:
        idx = skip_pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker)
        worksheet.update_cell(current_row, 3, pickvals[picker]['points']/pickvals[picker]['count'])
        worksheet.update_cell(current_row, 4, pickvals[picker]['total'])
        worksheet.update_cell(current_row, 5, pickvals[picker]['count'])
        worksheet.update_cell(current_row, 6, pickvals[picker]['points'])
        current_row+=1    
    return True

def post_results(week_id):
#   results=get_results(event_id)
    if not week_id:
        week_id=str((current_year()-2000)*100+current_week())
    results=json_results(results_api+str(week_id))
    worksheet=open_worksheet('Majors','Results')
    #get date and week number from header
    results_week=str(results['results'][0]['Week'])
    worksheet_week=str(worksheet.acell('I2').value)
    # check if update required
    if (results_week==worksheet_week):
        return False
    # Update points per player
    points={picker:0 for picker in skip_pickers}
    # Clear worksheet
    cell_list = worksheet.range('A2:J40')
    for cell in cell_list:
        cell.value=''
    worksheet.update_cells(cell_list)
    current_row=2
    for event in results['results']:
        worksheet.update_cell(current_row, 1, 'Event:')
        worksheet.update_cell(current_row, 2, event.get('Event Name'))
        worksheet.update_cell(current_row, 7, event.get('Year'))
        worksheet.update_cell(current_row, 8, 'Week:')
        worksheet.update_cell(current_row, 9, event.get('Week'))
        current_row+=1
        for player in event['Results']:
            worksheet.update_cell(current_row, 1, player['Rank'])
            worksheet.update_cell(current_row, 2, player['Name'])
            worksheet.update_cell(current_row, 3, player['R1'])
            worksheet.update_cell(current_row, 4, player['R2'])
            worksheet.update_cell(current_row, 5, player['R3'])
            worksheet.update_cell(current_row, 6, player['R4'])
            worksheet.update_cell(current_row, 8, player['Agg'])
            worksheet.update_cell(current_row, 9, player['Points'])
            if player.get('Picker'):
                worksheet.update_cell(current_row, 10, player['Picker'])
                points[player['Picker']]+=player['Points']
            current_row += 1
    # update points per picker
    pickers=skip_pickers
    if points[pickers[1]]>points[pickers[0]]:
        pickers.reverse()
    current_row+=1
    for picker in pickers:
        idx = pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker)
        worksheet.update_cell(current_row, 9, points[picker])
        current_row+=1    
    return True

def update_results(event_id):
    results=get_results(event_id)
    worksheet=open_worksheet('Majors','Results')
    #get date and week number from header
    results_update=str(results['event']['Last Update'])
    worksheet_update=str(worksheet.acell('I2').value)
    # check if update required
    if (results_update==worksheet_update):
        return False
    # Update header information
    worksheet.update_cell(2, 2, results['event'].get('Name'))
    worksheet.update_cell(2, 8, 'Update:')
    worksheet.update_cell(2, 9, results_update)
    worksheet.update_cell(1, 1, 'Pos')
    worksheet.update_cell(1, 2, 'Player')
    worksheet.update_cell(1, 3, 'R1')
    worksheet.update_cell(1, 4, 'R2')
    worksheet.update_cell(1, 5, 'R3')
    worksheet.update_cell(1, 6, 'R4')
    worksheet.update_cell(1, 7, 'Today')
    worksheet.update_cell(1, 8, 'Total')
    worksheet.update_cell(1, 9, 'Points')
    worksheet.update_cell(1, 10, 'Picked By')
    # Update points per player
    points={picker:0 for picker in skip_pickers}
    # Clear worksheet
    cell_list = worksheet.range('A3:J40')
    for cell in cell_list:
        cell.value=''
    worksheet.update_cells(cell_list)
    current_row=3
    for player in results['players']:
        worksheet.update_cell(current_row, 1, player['Rank'])
        worksheet.update_cell(current_row, 2, player['Name'])
        worksheet.update_cell(current_row, 3, player['R1'])
        worksheet.update_cell(current_row, 4, player['R2'])
        worksheet.update_cell(current_row, 5, player['R3'])
        worksheet.update_cell(current_row, 6, player['R4'])
        if player.get('Time'):
            worksheet.update_cell(current_row, 7, player['Time'])
        else:
            worksheet.update_cell(current_row, 7, player['Today'])
        worksheet.update_cell(current_row, 8, player['Total'])
        worksheet.update_cell(current_row, 9, player['Points'])
        if player.get('Picker'):
            worksheet.update_cell(current_row, 10, player.get('Picker'))
            points[player['Picker']]+=player['Points']
        current_row += 1
    # update points per picker
    pickers=results['pickers']
    current_row+=1
    for picker in pickers:
        idx = pickers.index(picker)
        worksheet.update_cell(current_row, 1, idx+1)
        worksheet.update_cell(current_row, 2, picker['Name'])
        worksheet.update_cell(current_row, 9, picker['Points'])
        current_row+=1
    return True

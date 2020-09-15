import json,requests
from bs4 import BeautifulSoup

ta_base_url="https://www.tripadvisor.com"
ta_rest_url="/Restaurants-g60982-Honolulu_Oahu_Hawaii.html"
urls=[ta_rest_url]+['/Restaurants-g60982-oa'+str(o)+'-Honolulu_Oahu_Hawaii.html' for o in range(30,900,30)]

def rest_results(url):
    page=requests.get(ta_base_url+url)
    soup = BeautifulSoup(page.text,"html.parser")
    urls=[]
    if 'Restaurants' in url:
        for a in soup.findAll('a', href=True):
            if a["href"].startswith("/Restaurant_Review") and a["href"].endswith("html") and a["href"] not in urls:
                urls.append(a["href"])
        results=[{"url":url,"name":url.split('-')[4].replace('_',' ')} for url in urls[1:]]    
    elif 'Restaurant_Review' in url:
        rdata=json.loads(soup.find('script', type='application/ld+json').string)
        results={t:rdata[t] for t in rdata.keys() if not(t.startswith('@'))}
        results['address']=results['address']['streetAddress']
        for t in  {s.text for s in soup.find('div',{"class":"bk7Uv0cc"}).findAll('span')}:
            if t.startswith("$"):
                results['costcat']=t[1:]
            elif t.startswith("#"):
                results["rank"]=t.split()[0]
            elif t.startswith("+"):
                results["phone"]=t[3:]
    return results

def get_restaurants(detail=False):
    rests=[]
    for url in urls:
        for r in rest_results(url):
            r['position']=len(rests)+1
            if detail:
                s=rest_results(r['url'])
                for p in s.keys():
                    r[p]=s[p]
            rests.append(r)
		
def get_restaurant_details(url):
    s=rest_results(r['url'])

import json,requests
from bs4 import BeautifulSoup

ta_base_url="https://www.tripadvisor.com"
ta_rest_url="/Restaurants-g60982-Honolulu_Oahu_Hawaii.html"
urls=[ta_rest_url]+['/Restaurants-g60982-oa'+str(o)+'-Honolulu_Oahu_Hawaii.html' for o in range(30,120,30)]

def soup_results(url):
    page=requests.get(ta_base_url+url)
    soup = BeautifulSoup(page.text,"html.parser")
    urls=[]
    if 'Restaurants' in url:
        for a in soup.findAll('a', href=True):
            if a["href"].startswith("/Restaurant_Review") and a["href"].endswith("html") and a["href"] not in urls:
                urls.append(a["href"])
        results=[{"url":url,name:url.split('-')[4].replace('_',' ')} for url in urls[1:]]    
    elif 'Restaurant_Review' in url:
        rdata=json.loads(soup.find('script', type='application/ld+json').text)
        results={t:rdata[t] for t in rdata.keys() if not(t.startswith('@'))}
        results['address']=results['address']['streetAddress']
        if len(soup.findAll("span", {"class": "_15QfMZ2L"}))>0:
            results['phone']=soup.findAll("span", {"class": "_15QfMZ2L"})[0].a.text[-12:]
    return results

rests=[]
for url in urls:
    for r in soup_results(url):
        r['position']=len(rests)+1
        print(r['position'],r['name'])
        s=soup_results(r['url'])
        for p in s.keys():
            r[p]=s[p]
        rests.append(r)
		
for r in rests:
    if not r.get('phone'):
        s=soup_results(r['url'])
        r['address']=s['address']
        r['phone']=s.get('phone')
        print(r['position'],r['name'],r['phone'])

with open('restaurants.json', 'w') as outfile:
    json.dump(rests, outfile)

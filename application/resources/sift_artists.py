import json
import urllib

api_key = open('api_key.txt').read()

f_rv = open("already_visited.txt", "r")
visited=[]
content = f_rv.readlines()
for line in content:
    visited.append(line.replace("\n","").decode('utf-8'))


f_rv = open("related_words_2_sifted.txt", "r")
f = open("related_words.txt", "r")
related_words = []

content = f.readlines()
for line in content:
    related_words.append(line)

content = f_rv.readlines()
for line in content:
    if line not in related_words:
        related_words.append(line)
# text_r = open('suspicious_artists.txt').readlines()
# last_artist = text_r[-1].split(" ")[0]
f_s = open("suspicious_artists.txt", "w")

# enter = False
for query in visited:
    # print type(query), type(last_artist.decode('utf-8'))
    # print query == last_artist.replace("\n","").decode('utf-8')
    # print query, last_artist
    # if query == last_artist.replace("\n","").decode('utf-8'):
    #     enter = True
    #     print True
    # if not enter:
    #     continue
    # print "Imhere"
    print "----------- "+query+" -------------"
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query.encode('utf8'),
        'limit': 1,
        'indent': True,
        'key': api_key,
    }
    url = service_url + '?' + urllib.urlencode(params)
    # print url
    response = json.loads(urllib.urlopen(url).read())
    if not response.get('itemListElement'):
        f_s.write(query.encode('utf8') + " | None"+"\n")
        continue
    for element in response['itemListElement']:
        el = element['result'].get('description')
        print el
        if el and el+"\n" not in related_words:
            print el, query.encode('utf8')
            f_s.write(query.encode('utf8') +" | "+ el.encode('utf8') + "\n")
            print "----->> " +query.encode("utf8") + " | " + el.encode("utf8")+"<<------" + "\n"
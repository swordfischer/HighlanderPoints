from email.utils import formatdate
from enum import unique
import requests
import re
import urllib.request
import time
import json
from itertools import chain
from bs4 import BeautifulSoup


urls = {
    "Australian": 'https://7ph.com.au/',
    "Canadian": 'https://www.canadianhighlander.ca/points-list/',
    "European": 'http://highlandermagic.info/banned-list/',
    "Scandinavian": 'https://raw.githubusercontent.com/swordfischer/ScandinavianHighlanderPointsList/master/PointsList.json'
}

vintageBan = 'https://api.scryfall.com/cards/search?q=banned%3Avintage&unique=cards'
formatBanned = json.loads(requests.get(vintageBan).text)
bannedCards = []
for card in formatBanned['data']:
    bannedCards.append(card['name'])

formatData = {}

for format in urls:
    formatData[format] = {} 
    url = urls[format]
    response = requests.get(url)
    soup = BeautifulSoup(response.text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'"), "html.parser")
    if format == 'Australian':
        for column in soup.find_all('h5'):
            point = re.sub(' .*', '', column.get_text())
            child = column.find_next('p').stripped_strings
            for card in child:
                print(point + ' ' + card)
                formatData[format][card] = point

    if format == 'Canadian':
        for card in soup.find_all('tr')[1::]:
            td = card.find_all('td')
            formatData[format][td[0].get_text()] = td[1].get_text()

    if format == 'European':
        content = soup.find('div', {"class": "post-content"})
        cards = content.find_all('div', {'class': 'vc_row'})[1]
        
        for card in cards.find_all('li'):
            if not card.parent('del'):
                formatData[format][card.get_text()] = 'Banned'

    if format == 'Scandinavian':
        list = json.loads(response.text)['pointsList']
        for category in list:
            for card in list[category]:
                formatData[format][card] = list[category][card]
    
    if format != 'Scandinavian':
        for card in bannedCards:
            formatData[format][card] = 'Banned'

uniqueCards = []

for formatinfo in formatData:
    for card in [*formatData[formatinfo]]:
        uniqueCards.append(card)

cardInformation = {}

for card in sorted(set(uniqueCards)):
    cardInformation[card] = []
    for format in formatData:
        if card in formatData[format].keys():
            point = formatData[format][card]
        else:
            point = '-'
        cardInformation[card].append(str(point))

for format in formatData:
    file = open(format + '.json', 'w')
    file.write(json.dumps(formatData[format]))
    file.close()

file = open('full.json', 'w')
file.write(json.dumps(cardInformation))
file.close()

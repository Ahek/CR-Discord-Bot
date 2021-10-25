import requests
import pandas as pd
import numpy as np
import time
from datetime import date

clantag = "PLACE YOUR CLANTAG HERE

CRTOKEN = "PLACE YOUR GENERATED TOKEN FROM DEVELOPER.CLASHROYALE.COM HERE"

clanname = "PLACE YOUR CLANNAME HERE, MAKE SURE IT'S EXACTLY THE SAME"

my_headers = {'Authorization' : f'Bearer {CRTOKEN}'}

data = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{clantag}", headers = my_headers).json()['memberList']

df = pd.DataFrame(data) #Dataframe with data from the request
df['arena'] = [x['name'] for x in df['arena']]

wardata = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{novauk3}/riverracelog", headers = my_headers).json()['items']
standings = [week['standings'] for week in wardata]

warstats = []

for week in standings:
    for rank in week:
        clan = rank['clan']['name']
        if clan == clanname:
            warstats.append(rank['clan']['participants'])
            break
            
name = [[player['name'] for player in week] for week in warstats] #List of names in the clan
fame = [[player['fame'] for player in week] for week in warstats] #List of gotten fame in war for each player
tag = [[player['tag'] for player in week] for week in warstats] #List of playertags

df_name = pd.DataFrame(data = name, index = [f'Week {x+1}' for x in range(len(name))]).transpose()
df_fame = pd.DataFrame(data = fame, index = [f'Week {x+1}' for x in range(len(name))]).transpose()
df_tag = pd.DataFrame(data = tag, index = [f'Week {x+1}' for x in range(len(name))]).transpose()

df_eind = pd.DataFrame(data = [[np.nan] * 200]*len(tag), index = [f'Week {x+1}' for x in range(len(tag))]).transpose()

list_names = set()
for week in list(df_name.columns):
    for x in df_name[week].values.tolist():
        list_names.add(x)
        
list_tags = set()
for week in list(df_tag.columns):
    for x in df_tag[week].values.tolist():
        list_tags.add(x)

df_eind = pd.DataFrame(data = [[np.nan] * len(fame)]*len(list_tags))
#The empty dataframe that will get the data in it

df_eind.columns = [f'Week {x+1}' for x in range(len(tag))]
df_eind.index = list_tags #Gives rownames

def get_name(tag_hash):
#Takes a playertag with hash and returns the name. Has sleeptime to not be blocked
    if tag_hash is None:
        name = np.nan
    try:
        tag = tag_hash[1:]
    except TypeError:
        return np.nan
    time.sleep(1)
    try:
        name = requests.request("GET", f"https://api.clashroyale.com/v1/players/%23{tag}", headers = my_headers).json()['name']
    except KeyError:
        name = np.nan
    return name

def get_trophies(tag_hash):
#Takes a playertag with hash and returns the trophies. Has sleeptime to not be blocked
    if tag_hash is None:
        return np.nan
    try:
        tag = tag_hash[1:]
    except TypeError:
        return np.nan
    time.sleep(1)
    try:
        trophies = requests.request("GET", f"https://api.clashroyale.com/v1/players/%23{tag}", headers = my_headers).json()['trophies']
    except KeyError:
        trophies = np.nan
    return trophies

for week in range(len(name)):
    for clanplayer in range(len(df_eind.index)):
        for warplayer in range(len(name[week])):
            if df_eind.index[clanplayer] == tag[week][warplayer]:
                df_eind.iloc[clanplayer, week] = fame[week][warplayer]
#Adds all values in a forloop (might take some time)
                
df_eind['Name'] = [get_name(tag) for tag in df_eind.index]
df_eind['trophies'] = [get_trophies(tag) for tag in df_eind.index]

df_eind_index = df_eind.index.tolist()

clandata = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{clanname}", headers = my_headers).json()['memberList']
membertags = [x['tag'] for x in clandata]

df_members = df_eind.loc[df_eind.index.isin(membertags)]
#Delete this line if you also want players in the file that aren't in the clan

date = date.today().strftime("%d %B")
df_members.to_excel(f"War {date}.xlsx", sheet_name = clanname)
import requests
import pandas as pd

def get_crdata(clantag, CRTOKEN):
    my_headers = {'Authorization' : f'Bearer {CRTOKEN}'}              
    data = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{clantag[1:]}", headers = my_headers, timeout = 20).json()['memberList']
    wardata = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{clantag[1:]}/riverracelog", headers = my_headers, timeout = 20).json()['items']
    return {"data":data, "wardata":wardata}

def create_warcsv(clantag, CRTOKEN):
    '''
    This is the main function
    '''
    from datetime import date
    data = get_crdata(clantag, CRTOKEN)['data']
    wardata = get_crdata(clantag, CRTOKEN)['wardata']
    
    df = pd.DataFrame(get_crdata(clantag, CRTOKEN))
    
    df['arena'] = [x['name'] for x in df['arena']]
    
    standings = [week['standings'] for week in wardata]
    
    #flatten the data and select only the clanresults where the clan has our tag. Then take of that the tag and fame for every player in theclan_flattened_keyval
    flattened = [pd.json_normalize(s) for s in standings]
    theclan = [week.query("`clan.tag` == @clantag") for week in flattened]
    theclan = pd.concat(theclan)['clan.participants']
    theclan_flattened = [pd.json_normalize(player) for player in theclan]
    theclan_flattened_keyval = [week.loc[:, ['tag', 'fame']] for week in theclan_flattened]
    theclan_flattened_keyval = [week.set_index('tag') for week in theclan_flattened_keyval]
    #Put all weeks together in 'samen'
    samen = pd.concat(theclan_flattened_keyval, axis = 1, join = 'outer')
    
    #Because the name was already together with tag in 'theclan_flattened', we create a dictionairy out of these two
    #This way we don't need to make another request for every single player
    allnames = []
    for df in theclan_flattened:
        allnames = allnames + df['name'].to_list()
    alltags = []
    for df in theclan_flattened:
        alltags = alltags + df['tag'].to_list()
    zip_iterator_name = zip(alltags, allnames)
    tagtoname = dict(zip_iterator_name)
    
    samen['Username'] = samen.index.map(lambda x: tagtoname[x])
    
    #'samen' has everyone who once participated in war, 'samen_clanmembers' has only people who are in the clan at that moment
    membertags = [member['tag'] for member in data]
    samen_clanmembers = samen.loc[samen.index.isin(membertags)]
    samen_clanmembers['trophies'] = [tagtotrophies(tag, CRTOKEN) for tag in samen_clanmembers.index]
    
    date = date.today().strftime("%d %B")
    samen_clanmembers.to_excel(f"War {date}.xlsx", sheet_name = clantag)
    return samen_clanmembers

def tagtotrophies(tag, CRTOKEN):
    data = get_crdata(tag, CRTOKEN)['data']
    membertags = [player['tag'] for player in data]
    membertrophies = [player['trophies'] for player in data]

    zip_iterator_trophies = zip(membertags, membertrophies)
    dict_tagtotrophies = dict(zip_iterator_trophies)
    try:
        return dict_tagtotrophies[tag]
    except KeyError:
        return None

class CRPlayer:
	def __init__(self, tag):
		self._tag = tag
		profiledata = requests.request("GET", f"https://api.clashroyale.com/v1/players/%23{self._tag}", headers = my_headers).json()
		self._name = profiledata['name']
		self._trophies = profiledata['trophies']
		self._ccwins = GetChallengeWins(profiledata)[0]
		self._gcwins = GetChallengeWins(profiledata)[1]
		try:
			self._LastSeasonBest = profiledata['leagueStatistics']['previousSeason']['bestTrophies']
		except KeyError:
			self._LastSeasonBest = "<5000"
		try:
			self._CurrentSeasonBest = profiledata['leagueStatistics']['currentSeason']['bestTrophies']
		except KeyError:
			self._CurrentSeasonBest = "<5000"
		self._PersonalBest = profiledata['bestTrophies']
		
	async def stats(self, msg):
		await msg.channel.send(f'Name: {self._name} \nClassic Challenge Wins: {self._ccwins} \nGrand Challenge Wins: {self._gcwins} \nLast Season Best: {self._LastSeasonBest} \nSeason Best: {self._CurrentSeasonBest} \nPersonal Best: {self._PersonalBest}')

class CRClan:
	def __init__(self, tag):
		self._tag = tag
		self._clandata = requests.request("GET", f"https://api.clashroyale.com/v1/clans/%23{self._tag}", headers = my_headers).json()
		self._requiredtrophies = self._clandata['requiredTrophies']
		self._membercount = len(self._clandata['memberList'])
		self._membertrophies = [x['trophies'] for x in self._clandata['memberList']]
	def requiredtrophies(self):
		return self._requiredtrophies
	def mediantrophies(self):
		return round(median(self._membertrophies))
	def fun_memberscount(self):
		return self._membercount

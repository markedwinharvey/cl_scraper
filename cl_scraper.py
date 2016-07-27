#!/usr/bin/env python 
'''
Scrape craiglist data for post frequency estimates using requests module and the html parser
BeautifulSoup. Autosaves csv data with timestamped filename. 
'''
import requests
import sys
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime as dt
from random import random as rand

cats = {
	'm4w': 'search/m4w',
	'free': 'search/zip',
	'w4m': 'search/w4m',
	'pets': 'search/pet',
	'cas_w4m': 'search/cas?query=w4m',
	'cas_m4w': 'search/cas?query=m4w',
	'cas_m4m': 'search/cas?query=m4m',
	'cas_w4w': 'search/cas?query=w4w',
	'm4m': 'search/m4m'
	
}

#-------- class declarations --------#
class nation():
	def __init__(self,name):
		self.name=name
		self.states = {}	

class state():
	def __init__(self,name,nation):
		self.name=name
		self.substates = {}
		self.nation = nation

class substate():
	def __init__(self,name,url):
		self.name=name
		self.url=url

#-------- function declarations --------#		
def exit():
	print;print 'Exiting...';print;sys.exit()
	
def show_nation(nation):
	print nation.name
	for each_state in nation.states:
		print ' ',each_state.name
		for each_substate in each_state.substates:
			print '   ',each_substate.name,each_substate.url

def make_usa(soup):
	usa = nation('United States')
	state_dat = soup.find('h1').find_next('div').contents

	for section in state_dat:
		this_section = bs(str(section))
		state_list = [bs(str(x)).get_text() for x in this_section.find_all('h4')]
		substate_list = [bs(str(x)).find_all('li') for x in this_section.select('h4 ~ ul')]
		for iter in range(len(state_list)):
			st = state(name=state_list[iter],nation=usa)
			usa.states[state_list[iter]] = st
			for each_subst in substate_list[iter]:
				subst = each_subst.find('a')
				url = 'https:'+str(subst.get('href'))
				if not url.endswith('org/'):
					continue
				sub_name = subst.get_text()
				subst = substate(url=url,name=sub_name)
				st.substates[sub_name] = subst
	return usa

def get_page(url):
	r = requests.get(url)
	return r.text


def scrape(filename, state_name, substate_name, base_url, cat):
	
	url = base_url + cats[cat]
	
	page=requests.get(url).text
	
	page = bs(page)
	total_count = page(attrs={'class': 'totalcount'})

	if total_count:
		total_count = int(total_count[0].get_text())
		times = page.find_all('time')
	
		time1 = times[0].get('datetime')
		if total_count > 100:
			if total_count % 100 == 0:
				check_end = total_count - 100
			else:
				check_end = total_count - (total_count % 100)
			if '?' not in url:
				url = url+'?s='+str(check_end)
			else:
				url_mod = url.split('?')
				url_start = url_mod[0]
				url_end = url_mod[1]
				
				#url = url_start + '?s='+str(check_end)+'&sort=date&'+url_end 
				url = url_start + '?s='+str(check_end)+'&'+url_end +'&sort=date'
				#sometimes the order matters!
				
				
			n=12+4*int(100*rand())/100.
			time.sleep(n)							#try to avoid the bot blockers
			
			page = bs(get_page(url))
			
			times = page.find_all('time')
			try:
				time2 = times[-1].get('datetime')
			except:
				print 'Failed on url:',url
			
		else:
			#total count on page < 100; need to extract last datetime before "nearby results"
			entries = page.select('.rows > *')		

			for i in entries:
				if i.find('time'):
					time2 = i.find('time').get('datetime')
				else:
					break
			
		time1 = str(time1).replace(' ','_')
		time2 = str(time2).replace(' ','_')
		
	else:
		total_count = 0; time2 = 'NA'; time1 = 'NA'

	
	new_data = ','.join([state_name, substate_name, url, str(total_count), time2, time1])
	with open('data/'+filename,'a') as f:			#append each entry to data file
		f.write(new_data+'\n')


def main():

	cat = 'cas_w4w'
	
	r = requests.get('https://www.craigslist.org/about/sites')
	page=r.text
	#with open('r','r') as f:
	#	page = f.read()
		
	time.sleep(4)
	soup = bs(page)
	
	usa = make_usa(soup)
	
	'''filename'''
	filename = str(dt.now()).split('.')[0].replace(' ','_')+'_'+cat
	'''filename'''
	
	index = 1
	for state in sorted(usa.states):
		for substate in sorted(usa.states[state].substates):
			sub = usa.states[state].substates[substate]
			print sub.name,sub.url
			
			#'''index'''
			if index > 0:						#for resuming collection when script fails from bad site data
			#'''index'''	
			
				scrape(
					filename=filename,
					state_name=state,
					substate_name=sub.name,
					base_url=sub.url,
					cat=cat
				)
		
				n=12+3*int(100*rand())/100.		
				time.sleep(n)					#try to avoid the bot blockers
			
			index+=1



if __name__ == '__main__':
	main()
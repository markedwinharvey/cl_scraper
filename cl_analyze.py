#!/usr/bin/env python
'''
cl_analyze.py processes and plots craigslist data (from csv) obtained using cl_scraper.py. 
Open and process data into data_sets (dictionary of data_set classes).
Each data_set class is a list of entries, one for each US city/area. 
Each csv line looks like this:
California,san francisco bay area,https://sfbay.craigslist.org/search/zip?s=2400,2500,2016-07-12_10:45,2016-07-16_21:36
	(state,substate,url,count,oldest post timestamp, newest post timestamp). 
Sort and plot 1D data. 
Plot permutations of 2D (vs.) data. Eliminate overt outliers, fit trendlines, and assess goodness-of-fit.
'''

import os
import sys
import operator
import subprocess as sp

import matplotlib as mpl
mpl.use('TkAgg')
mpl.rc('figure',facecolor='white')

import matplotlib.pyplot as plt

from pylab import rcParams
rcParams['figure.figsize'] = 12,9
rcParams.update({'figure.max_open_warning': 0})

import numpy as np

from decimal import Decimal
from datetime import datetime as dt

with open('ref/state_abbrev.txt') as f:
	state_abbrev = dict([x.split(',') for x in f.read().split('\n')])


#-------- class/data declarations --------#

data_sets = {}


class data_set():
	def __init__(self,name):
		self.name=name
		self.data = []
	def add(self,entry):
		self.data.append(entry)

		
class entry():
	def __init__(self,state,substate,url,count,delta_t,rate):
		self.state = state
		self.substate = substate
		self.url = url
		self.count = count
		self.delta_t = delta_t
		self.rate = rate


#-------- general functions --------#

def exit():
	print;print 'Exiting...';print;sys.exit()


def get_epoch(time_entry):
	'''Example time format (string): 2016-07-20_22:25'''
	
	t = time_entry.split('_')
	t = [int(x) for x in t[0].split('-') + t[1].split(':')]
	
	return int(dt(*t).strftime('%s'))	


def get_abbrev(state):
	'''access state abbreviation dictionary'''
	try:
		return state_abbrev[state]
	except:
		return state


def sort_and_save_r2(r2_rank):
	''' Sort 'vs.' plots by r-squared values (descending) and save as text file '''
	r2_rank_sorted = sorted(r2_rank,key=operator.itemgetter(0))[::-1]
	
	r2_rank_str=''
	for r in r2_rank_sorted:
		r2_rank_str += ','.join([str(x) for x in r])+'\n'
	
	with open('ref/r2_rank_sorted', 'w') as f:
		f.write(r2_rank_str)
			
			
#-------- processing functions --------#

def process(file_list):
	'''	Process each data_file (csv) in file_list; add to data_sets (dict)
		Each data_set (class) is a list of data entries
	'''
	for file in file_list:

		data_name = file.split('_')[-1]
		ds = data_set(name=data_name)
		
		with open(file,'r') as f:
			entry_list = [x for x in f.read().split('\n') if x]
			
		for line in entry_list:
			line = line.split(',')
			
			state 		= line[0]
			substate 	= line[1]
			url 		= line[2]
			count 		= int(line[3])
			
			if count != 0:
				t1 = get_epoch(line[4])
				t2 = get_epoch(line[5])
				delta_t = (float(t2)-t1)/60/60	#per day
				if delta_t != 0:
					rate = round(Decimal(1.*count/delta_t) , 2)
				else:
					rate = count	#count = 1; rate = 1/day
			else:
				delta_t = 0.
				rate = 0.
	
			e = entry(
				state		= state,
				substate	= substate,
				url			= url,
				count		= count,
				delta_t		= delta_t,
				rate		= rate
			)
			ds.add(e)
		data_sets[data_name] = ds


def get_outliers(d1,d2,dx_rates,dy_rates):
	'''Assess outlier data points and return information'''
	
	outliers 		= []
	outlier_idx 	= []
	outlier_point 	= []	
	
	d1_rate_sort = sorted([x for x in d1],key=lambda y: y.rate)
	if d1_rate_sort[-1].rate / d1_rate_sort[-2].rate > 3:
		outliers.append(d1_rate_sort[-1].substate)
	d2_rate_sort = sorted([x for x in d2],key=lambda y: y.rate)
	if d2_rate_sort[-1].rate / d2_rate_sort[-2].rate > 3:
		outliers.append(d2_rate_sort[-1].substate)
	
	if outliers:
		for o in outliers:
			outlier_idx.append([x.substate for x in d1].index(o))
			outlier_point.append((round(dx_rates[outlier_idx[-1]],1),round(dy_rates[outlier_idx[-1]],1)))
			
	return outliers,outlier_idx,outlier_point


#-------- plotting functions --------#

def make_single_plots():
	''' Plot top 30 highest-frequency posting areas for each category'''
	
	for i in data_sets.keys():
	
		d = data_sets[i].data
		sorted_d = sorted(d,key=operator.attrgetter('rate'))
		num_el = 30		#change num here
		trunc_d = sorted_d[len(d)-num_el:]
		
		fig = plt.figure()
		ax=fig.add_subplot(111)
		ax.set_title('US craigslist posts per day in category %s (top %i areas)' %(i,num_el))
		ax.bar( range(num_el),[x.rate for x in trunc_d],color='red',width=.3 )
		ax.set_xticks(np.linspace(0,num_el,num_el+1))
		ax.set_xticklabels( [ str(x.substate+' , '+get_abbrev(x.state)) for x in trunc_d ],rotation=-45,ha='left',minor=False )
		plt.tight_layout()
		
		filename = '%s_top30_fig.png'%(i)
		
		'''show or save'''
		plt.show()
		#plt.savefig('data/figs/indiv/'+filename)
		
		print filename,'processed'
			
				
def make_vs_plots():
	'''	Generate all permutations of vs. plots for available data
		Display data such that trendline slope >= 1'''
		
	r2_rank = []
	
	dataset_list = [x for x in sorted(data_sets.keys())]

	for i in range(len(dataset_list)-1):
		
		for j in range(i+1,len(dataset_list)):
					
			#-----organize data sets
			d1_name = dataset_list[i]
			d1 = data_sets[d1_name].data
			d1_rates = np.array([x.rate for x in d1])
	
			d2_name = dataset_list[j]
			d2 = data_sets[d2_name].data
			d2_rates = np.array([x.rate for x in d2])
			
			
			#-----put larger set on y axis (slope > 1)
			if sum(d2_rates) > sum(d1_rates):
				dy_name = d2_name
				dy_rates = d2_rates
				dx_name = d1_name
				dx_rates = d1_rates
			else:
				dy_name = d1_name
				dy_rates = d1_rates
				dx_name = d2_name
				dx_rates = d2_rates
			
			
			#-----check for outlier
			outliers,outlier_idx,outlier_point = get_outliers(d1,d2,dx_rates,dy_rates)
			dx_rates = [dx_rates[x] for x in range(len(dx_rates)) if x not in outlier_idx]
			dy_rates = [dy_rates[x] for x in range(len(dy_rates)) if x not in outlier_idx]
			
			
			#----- plotting and trendline
			fig = plt.figure()
			ax = fig.add_subplot(111)
			
			ax.scatter(dx_rates,dy_rates)
						
			ax.set_title('US craigslist posts per day (by location) %s vs. %s' %(dy_name,dx_name))
			ax.set_xlabel('%s posts per day' %dx_name)
			ax.set_ylabel('%s posts per day' %dy_name)
			
			z,SSres,_,_,_ = np.polyfit(dx_rates,dy_rates,1,full=True)
			
			p = np.poly1d(z)
			m = round(Decimal(z[0],2))
			b = round(Decimal(z[1],2))
			
			dy_mean = sum(dy_rates)/len(dy_rates)
			SStot = sum( (dy_rates - dy_mean)**2 )
			r2 = round(float(1-SSres/SStot),2)		#r-squared = 1- residual sum of squares(func) / total sum of squares(avg)
			
			if outliers:
				outliers_label = '\n'.join([ str(outliers[x]+' ('+str(outlier_point[x])+')') for x in range(len(outliers))])
			else:
				outliers_label = None
							
			ax.plot(dx_rates,p(dx_rates),
				label='y = '+str(m)+'x + '+str(b)+'\n r2 = '+str(r2)+ 
				'\n Outliers: '+ str(outliers_label)
			)
			
			#-----selective labeling for values > threshold
			dx_thresh = sorted(dx_rates)[-10]	#(highest 10 values)
			dy_thresh = sorted(dy_rates)[-10]
			
			labels = [d1[x].substate for x in range(len(d1)) if x not in outlier_idx]
			
			for k in range(len(labels)):
				if dx_rates[k] > dx_thresh or dy_rates[k] > dy_thresh:
					plt.annotate(
						labels[k],
						xy = (dx_rates[k],dy_rates[k])
					)
	
			ax.legend(loc='upper left')
			plt.tight_layout()
			
			
			filename = 'data/figs/vs/%s_vs_%s_fig.png' %(dy_name,dx_name)
			r2_rank.append([r2,filename])
			
			'''show or save'''
			plt.show()
			#plt.savefig(filename)
			
			print '%s_vs_%s processed' %(dy_name,dx_name)
			
	sort_and_save_r2(r2_rank)
	
	
#-------- open from saved data - functions --------#

def get_saved_r2():
	''' Open r-squared doc ('vs.' plot values sorted by r-squared) and open entries > threshold '''
	with open('ref/r2_rank_sorted','r') as f:
		r2_rank_sorted = [[float(x.split(',')[0]),x.split(',')[1]] for x in f.read().split('\n') if x]
	for each_entry in r2_rank_sorted:
		if each_entry[0] > 0.6:		#change r-squared threshold here
			sp.Popen(['open',each_entry[1]])


#-------- main function --------#
		
def main():
	file_list = sp.Popen(['ls','data'],stdout=sp.PIPE).communicate()[0].split('\n')
	file_list = ['data/'+x for x in file_list if x.startswith('2016')]

	process(file_list)	# data is accessible as data_sets['set_name'].data

	#--- plotting ---#
	make_single_plots()
	
	make_vs_plots()
	
	#get_saved_r2()
	
	
	

if __name__ == '__main__':
	main()
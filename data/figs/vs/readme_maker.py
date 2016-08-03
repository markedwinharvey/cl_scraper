#!/usr/bin/env python

import subprocess as sp

def main():
	#file_list = sp.Popen(['ls'],stdout=sp.PIPE).communicate()[0].split('\n')
	
	with open('../../../ref/r2_rank_sorted','r') as f:
		file_list = [x.split(',')[1] for x in f.read().split('\n') if x]
		file_list = [x.split('/')[-1] for x in file_list]

		
	for file in file_list:
		
		insertion = '![%s](https://github.com/markedwinharvey/cl_scraper/blob/master/data/figs/vs/%s)'%(file.split('.')[0],file)+'\n'
		
		with open('readme.md','a') as f:
			f.write(insertion)
		

if __name__ == '__main__':
	main()
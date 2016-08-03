#!/usr/bin/env python

import subprocess as sp
#![sample data](https://github.com/markedwinharvey/cl_scraper/blob/master/data/figs/vs/m4w_vs_w4m_fig.png)

def main():
	file_list = sp.Popen(['ls'],stdout=sp.PIPE).communicate()[0].split('\n')
	print file_list
	
	for file in file_list:
		
		
		
		if not file.endswith('png'):
		
			continue
		
		insertion = '![%s](https://github.com/markedwinharvey/cl_scraper/blob/master/data/figs/indiv/%s)'%(file.split('.')[0],file)+'\n'
		
		with open('readme.md','a') as f:
			f.write(insertion)
		
	
	
	
	
	pass
if __name__ == '__main__':
	main()
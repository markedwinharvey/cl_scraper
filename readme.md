<h4>cl_scraper</h4>

<h5>cl_scraper.py</h5>

Scrape craigslist data for frequency analysis using requests module and the html parser
BeautifulSoup. Data is actively appended to timestamped csv file as it is accessed. 

<h6>Usage:</h6>

	python cl_scraper.py

The category is specified within the main function; the appropriate url is formulated
based on a category dictionary. 


<h5>cl_analyze.py</h5>

Automatic plot generation from available data, using numpy and matplotlib. 
Individual plots show top 30 highest-frequency posting areas. <br>
2D plots, based on all permutations of available  data, are generated and fit with trendlines. 

<h6>Usage:</h6>

	python cl_analyze.py


Sample auto-generated 2D plot with trendline:

![sample data](https://github.com/sigmeh/cl_scraper/blob/master/data/figs/vs/m4w_vs_w4m_fig.png)

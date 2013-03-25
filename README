==Wait or Walk==
Author: Hunter Scott

A webapp to answer the question you really have at the bus stop: should I wait or should I walk? Scrapes Nextbus (since their public API isn't open for every location, including Georgia Tech) and uses the Google Maps API to calculate walking times and distances.

Uses the awesome jQuery Mobile Bootstrap theme by Andy Matthews.

Only supports the blue and red routes at Georgia Tech right now, but next on my list is the Trolley. There are some less than elegant parts of this code because of rate limiting. The Google distance matrix API has some terms of use and a pretty short request limit, so the distance matrix can be generated with generate_distance_matrix.py. The code then uses the json files it generates to do offline walking and driving time calculations. The weather API also has a rate limit, so updates are only called once every 5 minutes. 


Installation:
sudo pip install flask
sudo pip install beautifulsoup
How to deploy with Apache: http://www.subdimension.co.uk/2012/04/24/Deploying_Flask_to_Apache.html

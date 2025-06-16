# HLTV
Python project to get HLTV data

idea is that this should act as a black box
user should create a class(ex: HLTV), put in the input arguments(ex: queriesPerSecond), and then be able to call whatever is needed from that class

THE USER SHOULDN'T BE REQUIRED TO HANDLE ANY SPECIAL CASES, THIS IS A BLACK BOX
This means that if we're gonna scrape, we gotta implement the throttling here

### ToDos
Get headless browser working

Enforce that all scrapes must go through the rate limiter

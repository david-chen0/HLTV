# HLTV
Python project to get HLTV data

idea is that this should act as a black box
user should create a class(ex: HLTV), put in the input arguments(ex: queriesPerSecond), and then be able to call whatever is needed from that class

THE USER SHOULDN'T BE REQUIRED TO HANDLE ANY SPECIAL CASES, THIS IS A BLACK BOX
This means that if we're gonna scrape, we gotta implement the throttling here

### ToDos
Use a DB to store scraped results
This can lower the number of scrapes we need to make, but we also need to make checks to make sure that our data doesn't still go stale.
Still helpful though. Ex: Call to get team by name(Spirit) would usually require us to get all teams, then get the ID of the team matching the name Spirit.
Instead, we can just get the ID of Spirit from the DB and then query HLTV using that
We'll also need to evict time-based data very aggressively from the DB if we plan to store it in there at all

Change get_team to get the players and coach from roster rather than top box

Add scraping for coach data

Auto-click Cloudflare's bot protection button("Click to confirm you're human" button), might not be possible(CloudFlare probably detects this)

Get headless browser working(might not be possible due to Cloudflare's bot protection)

Enforce that all scrapes must go through the rate limiter

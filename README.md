# Atom8-Scrape
### atom8-scrape

atom8-scrape is a utility built for scraping images from social media websites/threads/profiles. With it you can specify conditions, scrape from multiple locations, and export your scraped images to a specific directory.

### atom8-scrape-gui

atom8-scrape-gui is a GUI frontend for atom8-scrape. With it you are able to:
 - create & manage scrape settings
 - run atom8-scrape using your configured settings

## Integrations
 - Instagram
 - Reddit
 - TIGSource
 - Tumblr
 - Twitter

#### Pending
 - Facebook
 - Pinterest

## Usage

atom8-scrape requires that you create a configuration file. This file specifies what pages are being targeted by the scraper as well as various constraints to apply. ___\*documentation for this hasn't been written yet.. sorry\*___.

	atom8-scrape [OPTIONS] [SETTINGS] [TARGET]
		-v 		verbosity
		-d 		depth		How many days to scrape
		-e 		exportdest	Directory to export scrape to

		SETTINGS 	the settings file to use for this scrape
		TARGETS		the platforms to target in this scrape (must be specified by settings already)

#### ex:
	atom8-scrape -v -d 5 -e ~/Downloads mysettings instagram twitter


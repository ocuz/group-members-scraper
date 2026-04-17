# group members scraper

This is a script that:
- uses the roblox groups API endpoint to scrape all members of a specific roblox group with their group ID
- uses pagination cursors
- writes in a csv file
- writes cursors in a txt file
- safety measure incase of a crash (start from custom cursor)

How to use:
- have python installed + added to path
- on your codespace do "cd C:\folder\path\where\the\script\is"
- do "pip install requests"
- do "py main.py" or "python main.py" to run the script
- type 1 or 2 to choose mode
- put group id

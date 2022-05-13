# Kapsar.py

```Kapsar.py``` is a simple Python script for archiving and analyzing Pocket/Read It Later reading history.



Dependencies: ```newspaper3k``` and ```pandas```. (Plus Python, of course.)



Just place the script in the same folder as your ```ril_export.html``` file you can get at [http://getpocket.com/export](http://getpocket.com/export).



To download your archived links, run ```kapsar.py -a```. The articles will be saved in year/month folders both in html and plain text formats. This may take a few nights. You can interrupt the script any time with CTRL+BREAK. (Don't try CTRL+C, as it will skip the current article and log it as a succesfull download -- something you want to avoid.)



Failed downloads get logged, too. If you want to give them another shot, run ```kapsar.py -r```.



Curious about various stats? Run ```kapsar.py -s``` and enjoy your CSVs.



Why [Kapsář](https://en.wiktionary.org/wiki/kaps%C3%A1%C5%99)?
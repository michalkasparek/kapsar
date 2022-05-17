# Kapsar.py

```Kapsar.py``` is a simple Python script for archiving and analyzing Pocket/Read It Later reading history.



Dependencies: ```Newspaper3k``` and ```Pandas```. (Plus Python, of course.)



Just place the script in the same folder as your ```ril_export.html``` file obtained at [http://getpocket.com/export](http://getpocket.com/export).



To download archived links, run ```kapsar.py -a```. Articles will be saved in year/month folders both in HTML and plain text. This may take a few nights. You can interrupt the script any time with CTRL+BREAK and resume it later. (Don't try CTRL+C, as it will skip the current article and log it as a succesfull download -- something you want to avoid.)



If you want to give your failed downloads another shot, run ```kapsar.py -r```.



Curious about various stats? Run ```kapsar.py -s``` and enjoy your CSVs. (Nothing gets downloaded so this takes only a few seconds.)



Why [Kapsář](https://en.wiktionary.org/wiki/kaps%C3%A1%C5%99)?
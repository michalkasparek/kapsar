#!/usr/bin/env python

"""
A simple tool for downloading all the articles you've ever read in Pocket (formerly Read It Later). 
Just place the script in the same folder as your ril_export.html file. (You can get it at http://getpocket.com/export.)

__version__ = "0.1.1"
__author__ = "Michal Kašpárek"
__email__ = "michal.kasparek@gmail.com"
__license__ = "MIT"
__status__ = "prototype"
"""

import datetime
import requests
from lxml.html import fromstring
import re
import sys
import os
from newspaper import Article
import pandas as pd

def directory(directory):
    if os.path.exists(directory):
        pass
    else:
        os.makedirs(directory)

def getAllLines():

    try:
        with open("ril_export.html", mode="r", encoding="utf-8") as pocketExport:
            pocketExport = pocketExport.read().split("<h1>Read Archive</h1>")[1].splitlines()
    except:
        print("Can't load ril_export.html. Get the file at http://getpocket.com/export and save it to the same folder as kapsar.py.")
        exit()

    allLines = []

    for line in pocketExport:
        if "<li><a href" in line:
            allLines.append(line)
        else: 
            pass

    return allLines

class Kapsar: # handles & downloads articles

    def __init__(self, cleanedURL, rawTimestamp):

        self.cleanedURL = cleanedURL
        self.savedOn = datetime.date.fromtimestamp(rawTimestamp)
        self.domain = cleanedURL.split("//")[1].split("/")[0].replace("www.", "")

    def steal(self):

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}

        try:

            self.content = requests.get(self.cleanedURL, timeout=3)
            
            self.path = os.path.join("archive", str(self.savedOn.year), str(self.savedOn.month))

            if self.content.status_code == 403 or 406:
                self.content = requests.get(self.cleanedURL, headers=headers)

            if self.content.status_code == 200:               
                
                if "application/pdf" in self.content.headers["Content-Type"]:
                    
                    self.filename = self.cleanedURL.split("/")[-1]

                    directory(self.path)
                    
                    with open(os.path.join(self.path, self.filename), mode="w+b") as file:
                        file.write(self.content.content)

                else:

                    try:
                        self.article = Article(self.cleanedURL)
                        self.article.download()
                        self.article.parse()
                        self.title = self.article.title
                        self.completeText = self.title + "\n\n" + self.cleanedURL + "\n\n" + ", ".join(self.article.authors) + "\n\n" + str(self.article.publish_date) + "\n\n" + str(self.article.text)
                    except:
                        tree = fromstring(self.content.content)
                        self.title = tree.findtext(".//title")
                        self.completeText = "3Kerror"

                    self.filename = re.sub("[^\w]", "_", self.title)
                    self.filename = self.domain + "_" + self.filename
                    self.filename = self.filename[0:128]

                    if os.path.exists(self.path):
                        pass
                    else:
                        os.makedirs(self.path)

                    with open(os.path.join(self.path, self.filename + ".html"), mode="w+", encoding="utf-8") as file:
                        file.write(str(self.content.text))

                    if self.completeText != "3Kerror":
                        with open(os.path.join(self.path, self.filename + ".txt"), mode="w+", encoding="utf-8") as file:
                            file.write(self.completeText)

            if self.content.status_code != 200:
                logError("error" + str(self.content.status_code), self.cleanedURL)

        except requests.exceptions.ConnectionError:
            logError("ConnectionError", self.cleanedURL)

        except requests.exceptions.ContentDecodingError:
            logError("ContentDecodingError", self.cleanedURL)

        except requests.exceptions.ChunkedEncodingError:
            logError("ChunkedEncodingError", self.cleanedURL)

        except requests.exceptions.ReadTimeout:
            logError("ReadTimeout", self.cleanedURL)

        except:
             logError("UknownError", self.cleanedURL)

def logError(error, url):
    errorFilename = error + ".txt"
    with open(os.path.join("log", errorFilename), mode="a+", encoding="utf-8") as errorFile:
        errorFile.write(url + "\n")

class Parse: # gets data from ril_export.html lines
    def __init__(self, line):
        self.rawPocketData = line.split("\"")
        self.rawURL = self.rawPocketData[1]
        self.rawTimestamp = int(self.rawPocketData[3])
        self.cleanedURL = self.rawURL.split("?")[0]
        self.domain = self.cleanedURL.split("//")[1].split("/")[0].replace("www.", "")
        self.savedOn = datetime.datetime.fromtimestamp(self.rawTimestamp)

def archive(): # parses all lines in ril_export.html, checks for already downloaded articles and downloads the rest in reversed order 

    directory("log")

    try:
        with open(os.path.join("log", "archived.txt"), mode="r", encoding="utf-8") as archived:
            archived = archived.read().splitlines()
    except:
        archived = []

    newLines = []

    for x in allLines:
        parsedLine = Parse(x)
        if parsedLine.cleanedURL in archived:
            pass
        else:
            newLines.append([parsedLine.cleanedURL, parsedLine.rawTimestamp])
    
    lineByLine(newLines, False)

def retry():

    retryURLs = []
    retryLines = []
    directory("log")

    for filename in os.listdir("log"):
        if filename != "archived.txt":
            with open(os.path.join("log", filename), 'r') as f:
                f = f.readlines()
                for line in f:
                    retryURLs.append(line[0:-1])
        else:
            pass

    for line in allLines:
        parsedLine = Parse(line)
        if parsedLine.cleanedURL in retryURLs:
            retryLines.append([parsedLine.cleanedURL, parsedLine.rawTimestamp])

    lineByLine(retryLines, True)

def lineByLine(lines, retried):

    totalArticles = len(lines)
    progressArticles = 0    

    print(f"You can end the script safely anytime with CTRL+BREAK or simply closing the terminal window, and resume it later.\nCTRL+C will result in marking undownloaded articles as downloaded.\n\n{totalArticles} articles to download\n")

    for x in lines:
        progressArticles += 1
        cleanedURL = x[0]
        rawTimestamp = x[1]
        print(f"{progressArticles}/{totalArticles} {cleanedURL}")
        Kapsar(cleanedURL, rawTimestamp).steal()

        if retried == False:
            with open(os.path.join("log", "retried.txt"), mode="a+", encoding="utf-8") as archiveExpand:
                archiveExpand.write(cleanedURL + "\n")
        else:
            with open(os.path.join("log", "archived.txt"), mode="a+", encoding="utf-8") as archiveExpand:
                archiveExpand.write(cleanedURL + "\n")

    print("Done.")

def stats():

    print("Generating stats…")

    directory("stats")

    domainsAndDates = []

    for x in allLines:
        parsedLine = Parse(x)
        domainsAndDates.append([parsedLine.domain, parsedLine.savedOn.year, parsedLine.savedOn.month, parsedLine.savedOn.day, parsedLine.savedOn.strftime("%A"), pd.to_datetime(parsedLine.savedOn)])

    stats = pd.DataFrame(data = domainsAndDates, columns = ["domain", "year", "month", "day", "weekday", "timestamp"])
    stats.to_csv(os.path.join("stats", "rawStats.csv"))

    topSources = stats["domain"].value_counts().nlargest(100)
    topSources.to_csv(os.path.join("stats", "topSources.csv"))

    today = str(datetime.date.today())
    yesteryear = str(datetime.date.today() - datetime.timedelta(days=365))

    topSourcesLast365days = stats[(stats["timestamp"] > yesteryear) & (stats["timestamp"] < today)]
    topSourcesLast365days = topSourcesLast365days["domain"].value_counts().nlargest(50)
    topSourcesLast365days.to_csv(os.path.join("stats", "topSourcesLast365days.csv"))

    yearFrom = stats["year"].min()
    yearUntil = (stats["year"].max()) + 1

    for x in range (yearFrom, yearUntil):
        statsEachYear = stats[stats["year"] == x]
        statsEachYear = statsEachYear["domain"].value_counts().nlargest(50)
        statsEachYear.to_csv(os.path.join("stats", str(x) + ".csv"))

    articlesYearly = stats["year"].value_counts().sort_index()
    articlesYearly.to_csv(os.path.join("stats", "articlesYearly.csv"))

    articlesMonthly = stats.groupby(pd.Grouper(key="timestamp", freq="1M")).size()
    articlesMonthly.to_csv(os.path.join("stats", "articlesMonthly.csv"))

    sourcesYearly = stats.groupby("year").nunique()["domain"].transpose()
    sourcesYearly.to_csv(os.path.join("stats", "sourcesYearly.csv"))

    stats["time"] = stats["timestamp"].dt.time
    stats["time"] = pd.to_datetime(stats["time"].astype(str)).apply(pd.Timestamp)
    daytimes = stats.groupby(pd.Grouper(key="time", freq="5min")).size()
    daytimes.index = daytimes.index.strftime("%H:%M")
    daytimes.to_csv(os.path.join("stats", "daytimes.csv"))

    topDomains = topSources.index.values.tolist()

    topSourcesYearly = stats.loc[:, ["domain", "year"]]
    topSourcesYearly = topSourcesYearly[stats.domain.isin(topDomains)]
    topSourcesYearly = topSourcesYearly.groupby(["domain", "year"])["domain"].count().unstack()
    topSourcesYearly.to_csv(os.path.join("stats", "topSourcesYearly.csv"), float_format="%g")

    print("Done.")

if len(sys.argv) == 1:

    print("-a for archivation, -r to re-check the broken links, -s for stats")

else:

    allLines = getAllLines()

    if "-a" in sys.argv:
        archive()
    if "-r" in sys.argv:
        retry()
    if "-s" in sys.argv:
        stats()
import requests
import json
import matplotlib.pyplot as plt
from collections import Counter


def getFilmList(user):
    print(f"Getting film list for {user}...")
    filmList=[]
    i=1
    while True:
        print("Slurping account page "+str(i))
        content = requests.get(f"https://letterboxd.com/{user}/films/page/{i}/").content.decode("utf-8")
        i+=1
        contentsplit = content.split("data-target-link=\"/film/")
        for section in contentsplit:
            if "DOCTYPE html" in section: continue
            link = section.split("/")[0]
            filmList.append(link)
        if ">Older</a>" not in content: break
    print("End of film list reached.")
    return filmList


def getFromJSON(jsonData, category):
    try:
        list=[]
        for item in jsonData[category]:
            list.append(item)
        return list
    except:
        print(f"error in scraping JSON data for that movie's {category}")


def getFromHTML(content, fingerprint):
    list = []
    sections = content.split(fingerprint)
    sections.pop(0)
    for section in sections:
        item = section.split('>')[1].split('<')[0]
        list.append(item)
    return list


def crawlFilm(filmName):
    content = requests.get(f"https://letterboxd.com/film/{filmName}").content.decode("utf-8")
    jsonData = json.loads(content.split("/* <![CDATA[ */")[1].split("/* ]]> */")[0]) ## capturing convinient CDATA file in footer
    print(jsonData['name'])

    year = jsonData['releasedEvent'][0]['startDate']
    runtime = content.split("text-link text-footer\">")[1].split("&nbsp;mins")[0].strip()
    directors = getFromJSON(jsonData, 'director')
    actors = getFromJSON(jsonData, 'actors')
    writers = getFromHTML(content, '<a href=\"/writer/')
    cinematographers = getFromHTML(content, '<a href=\"/cinematography/')
    genres = getFromJSON(jsonData, 'genre')
    themes = getFromHTML(content, '/by/best-match/')
    rating = jsonData['aggregateRating']['ratingValue']

    for actor in actors:
        global actorsDic
        count = actorsDic[actor] if actor in actorsDic else 0
        actorsDic.update({actor:count+1})
    
    for director in directors:
        global directDic
        count = directDic[director] if director in directDic else 0
        directDic.update({director:count+1})
    
    for writer in writers:
        global writerDic
        count = writerDic[writer] if writer in writerDic else 0
        writerDic.update({writer:count+1})
    
    for cinema in cinematographers:
        global cinemaDic
        count = cinemaDic[cinema] if cinema in cinemaDic else 0
        cinemaDic.update({cinema:count+1})

    for genre in genres:
        global genresDic
        count = genresDic[genre] if genre in genresDic else 0
        genresDic.update({genre:count+1})

    for theme in themes:
        global themesDic
        count = themesDic[theme] if theme in themesDic else 0
        themesDic.update({theme:count+1})

    global years
    years.append(year)

    global runtimes
    runtimes.append(runtime)

    global ratings
    ratings.append(rating)


def sortNprintDic(dic):
    i = 10
    for count in sorted(dic, key=dic.get, reverse=True):
        print(count, dic[count])
        i -= 1
        if i == 0: break


actorsDic={}
directDic={}
writerDic={}
cinemaDic={}
genresDic={}
themesDic={}

years=[]
runtimes=[]
ratings=[]


def main():
    user = input("Enter letterboxd username > ")
    filmList = getFilmList(user)
    print("Crawling films...")
    for film in filmList:
        try:
            crawlFilm(film)
        except:
            print("error crawling that film")
    print("Finished crawling films.")

    print("Calculating stats now...")

    print("\n--TOP ACTORS--")
    global actorsDic
    sortNprintDic(actorsDic)

    print("\n--TOP DIRECTORS--")
    global directDic
    sortNprintDic(directDic)

    print("\n--TOP WRITERS--")
    global writerDic
    sortNprintDic(writerDic)

    print("\n--TOP CINEMATOGRAPHERS--")
    global cinemaDic
    sortNprintDic(cinemaDic)

    print("\n--TOP GENRES--")
    global genresDic
    sortNprintDic(genresDic)
    
    print("\n--TOP THEMES--")
    global themesDic
    sortNprintDic(themesDic)

    global years
    yearsFig = plt.figure()
    ax1 = yearsFig.add_subplot(1, 1, 1)
    n, bins, patches = ax1.hist(years)
    ax1.set_xlabel('release year')
    ax1.set_ylabel('Frequency')

    global runtimes
    runtimesFig = plt.figure()
    ax2 = runtimesFig.add_subplot(1, 1, 1)
    n, bins, patches = ax2.hist(runtimes)
    ax2.set_xlabel('runtime in minutes')
    ax2.set_ylabel('Frequency')
    
    global ratings
    ratingsFig = plt.figure()
    ax3 = ratingsFig.add_subplot(1, 1, 1)
    n, bins, patches = ax3.hist(ratings)
    ax3.set_xlabel('rating from 1-5')
    ax3.set_ylabel('Frequency')

    plt.show()


main()

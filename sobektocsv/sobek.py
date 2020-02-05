from bs4 import BeautifulSoup
import requests
from contextlib import closing
import re
import csv
from requests.exceptions import RequestException

def simple_get(url):
    try:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)
filename = "output.csv"
with open(filename, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
              
            # writing the fields 
            csvwriter.writerow(["objectid","cdmid","title","format","thumb","images","source","date","creator"])
i = 1
a = 1
while(i<39):
    page = "http://ncf.sobek.ufl.edu/formats/all/brief/"+str(i)
    raw_html = simple_get(page)
    html = BeautifulSoup(raw_html,'html.parser')
    theses = html.findAll("section", {"class": "sbkBrv_SingleResult"})

    for thesis in theses:

        images = []

        title = thesis.find("span", {"class": "briefResultsTitle"})
        print(title.text)
        tlink = title.find('a').get('href')

        imageCount = 1
        nextImage = True

        while nextImage:
            newraw_html = simple_get(tlink+'/00001/'+str(imageCount)+'j')
            newhtml = BeautifulSoup(newraw_html,'html.parser')
            image = newhtml.find('img', {"itemprop" : "primaryImageOfPage"}).get('src')
            images.append(image)
            if newhtml.find('span', {"class" : "sbkIsw_RightPaginationButtons"}):
                imageCount+=1
            else:
                nextImage = False

        print(imageCount)

        print(images)
        print(tlink)

        detaildiv = thesis.find("dl", {"class" : "sbkBrv_SingleResultDescList"})
        details = detaildiv.findAll("dd")

        student = details[0].text.strip()


        if "Date" in str(detaildiv):
            date = re.search(r"<dt>Date:</dt>.*?\n", str(detaildiv)).group(0)
            date = BeautifulSoup(date,'html.parser')
            date = date.findAll("dd")
            print(date)
            date = date[0].text.strip()


        if "Creator" in str(detaildiv):
            creator = re.search(r"<dt>Creator:</dt>.*?\n", str(detaildiv)).group(0)
            creator = BeautifulSoup(creator,'html.parser')
            creator = creator.findAll("dd")
            print(creator)
            creator = creator[0].text.strip()


        with open(filename, 'a') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
              
            # writing the fields 
            imagestext = ""
            for image in images[:-1]:
                imagestext = imagestext + image + ";"
            imagestext = imagestext + images[-1]
            imagethm = images[0];
            csvwriter.writerow(["special"+str(a),a,title.text,"image/jpeg",imagethm,imagestext,tlink,date,creator])
            a+=1

        print('----------------------------------')
    i+=1

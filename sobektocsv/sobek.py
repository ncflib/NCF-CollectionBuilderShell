from bs4 import BeautifulSoup
import requests
from contextlib import closing
import re
import time
from tqdm import tqdm
import csv
from requests.exceptions import RequestException
import os

os.system('cls')  # For Windows
os.system('clear')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    csvwriter.writerow(["objectid","cdmid","title","format","thumb","images","source","date","creator","subjects","generalnote","sourceofdescription"])

i = 1 # the current page number
a = 1 # the current number of the object



print(bcolors.OKBLUE + bcolors.BOLD)
print(bcolors.OKBLUE + "SOBEK TO CSV PYTHON SCRIPT \nNew College of Florida\nDigital Scholarship Studio\n~this feels like 90s" + bcolors.ENDC)

print("\nBefore you start, make sure you have the correct collectionname. ")
print("For example, collectionname is "+ bcolors.UNDERLINE + "affairs" + bcolors.ENDC + " if the link is http://ncf.sobek.ufl.edu/affairs/ \n")

COLLECTIONNAME = input("Enter the collection name: ") 

page = "http://ncf.sobek.ufl.edu/"+COLLECTIONNAME+"/all/brief/"+str(i) ## To get the number of total pages automatically
raw_html = simple_get(page)
html = BeautifulSoup(raw_html,'html.parser')
last = html.find('button', { "title" : "Last Page"})
if last != None:
	last = last.get('onclick')
	last = re.search(r"/all/brief/(.*)'; return false", last).group(1)
	NUMOFPAGES = int(last)
else:
	NUMOFPAGES = 1

print("COLLECTION: ", COLLECTIONNAME)
print("NUMBER OF PAGES: ", NUMOFPAGES)
print("OUTPUT FILE NAME: ",filename)
print(bcolors.OKGREEN)
print("\n")

pbar = tqdm(total=(NUMOFPAGES)*20)

for i in range(NUMOFPAGES):
    page = "http://ncf.sobek.ufl.edu/"+COLLECTIONNAME+"/all/brief/"+str(i)
    raw_html = simple_get(page)
    html = BeautifulSoup(raw_html,'html.parser')
    items = html.findAll("section", {"class": "sbkBrv_SingleResult"})

    for item in items:

        images = []
        subjects = []
        pdfs = [] # There is no compound PDFs but just in case.

        title = item.find("span", {"class": "briefResultsTitle"})
        tlink = title.find('a').get('href')

        imageCount = 1
        nextImage = True
        doctype = "image/jpeg"
        volume = False
        if "All Volumes" in str(simple_get(tlink)):
            volume = True
            links = list()
            newraw_html = BeautifulSoup(simple_get(tlink+'/allvolumes2/'),'html.parser')
            tables = newraw_html.findAll("table", {"class" : "sbkMviv_Thumbnail"})
            for table in tables:
                pdf = table.find('a').get('href')
                links.append(pdf)
            

            for link in links:
                newraw_html = simple_get(link)
                html = BeautifulSoup(newraw_html,'html.parser')
                pdf = html.find('a', { "id" : "sbkPdf_DownloadFileLink"}).get('href')
                pdfs.append(pdf)
                doctype = "application/pdf"

        else:
            while nextImage:

                if imageCount == 1:
                    newraw_html = simple_get(tlink+'/00001/')
                else:
                    newraw_html = simple_get(tlink+'/00001/'+str(imageCount)+'j')

                newhtml = BeautifulSoup(newraw_html,'html.parser')

                if newhtml.find('img', {"itemprop" : "primaryImageOfPage"}):
                    image = newhtml.find('img', {"itemprop" : "primaryImageOfPage"}).get('src')
                    images.append(image)
                    if newhtml.find('span', {"class" : "sbkIsw_RightPaginationButtons"}):
                        imageCount+=1
                    else:
                        nextImage = False

                elif newhtml.find('a', { "id" : "sbkPdf_DownloadFileLink"}):
                    pdf = newhtml.find('a', { "id" : "sbkPdf_DownloadFileLink"}).get('href')
                    pdfs.append(pdf)
                    doctype = "application/pdf"
                    nextImage = False
                    break;

        

        detaildiv = item.find("dl", {"class" : "sbkBrv_SingleResultDescList"})
        details = detaildiv.findAll("dd")

        if doctype == "application/pdf":
            imagethm = item.find("img", {"class" : "resultsThumbnail"}).get('src')

        if "Date" in str(detaildiv):
            date = re.search(r"<dt>Date:</dt>.*?\n", str(detaildiv)).group(0)
            date = BeautifulSoup(date,'html.parser')
            date = date.findAll("dd")
            date = date[0].text.strip()


        if "Creator" in str(detaildiv):
            creator = re.search(r"<dt>Creator:</dt>.*?\n", str(detaildiv)).group(0)
            creator = BeautifulSoup(creator,'html.parser')
            creator = creator.findAll("dd")
            creator = creator[0].text.strip()

        if "Subjects.Display" in str(detaildiv):
            subjects = re.search(r"<dt>Subjects.Display:</dt>.*?\n", str(detaildiv)).group(0)
            subjects = BeautifulSoup(subjects,'html.parser')
            subjects = subjects.findAll("dd")

        newraw_html = simple_get(tlink+'/00001/citation')
        newhtml = BeautifulSoup(newraw_html,'html.parser')

        generalnote=""
        notes = newhtml.findAll("dd", {"class": "sbk_CivGENERAL_NOTE_Element"})
        for note in notes:
            if note.find("span") and "This bibliographic record is available under the Creative Commons CC0 public" not in note.text:
                generalnote = note.text

        sourceofdescription=""
        sourceofdescriptions = newhtml.findAll("dd", {"class": "sbk_CivSOURCE_OF_DESCRIPTION_Element"})
        for source in sourceofdescriptions:
            if source.find("span"):
                sourceofdescription = source.text

        with open(filename, 'a') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
              
            if doctype == "image/jpeg":
                imagestext = ';'.join(images)
            else:
                imagestext = ';'.join(pdfs)
            subjects[:] = [s.text.strip().replace(" -- New College (Sarasota, Fla.)","") for s in subjects]
            subjectstext = ';'.join(subjects)

            if doctype == "image/jpeg":
                imagethm = images[0]

            if volume == True:
                index = 1
                for pdf in pdfs:
                    csvwriter.writerow(["special"+str(a),a,title.text + " - " + str(index),doctype,imagethm,pdf,tlink,date,creator,subjectstext,generalnote,sourceofdescription])
                    index=index+1
            a+=1

        pbar.update(1)
pbar.close()
print("\n DONE. Please check the csv file.")

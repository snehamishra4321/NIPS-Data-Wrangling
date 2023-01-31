from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import requests
import subprocess
import pdb
from tqdm import tqdm

from pdfminer.high_level import extract_text
import multiprocessing as mp

# Set to true if you want to download the paper to your local drive
DOWNLOAD_PAPERS = False

# Output directory
OUTPUT_PATH = "Output"

# Start Year
YEAR_MIN = 1988

# End Year
YEAR_MAX = 2022

# No: of Cores of CPU to be used
N_CORES = 20

# Total no: of papers extracted
total_papers = 0

# No: of papers with missing abstract
abstract_missing = 0

# No: of papers with missing text
text_missing = 0

# No: of papers with missing Author
author_missing = 0

base_url  = "https://proceedings.neurips.cc/"
index_urls = {1987: "https://proceedings.neurips.cc/paper/1987"}


def text_from_pdf(pdf_path, download_papers = False):

    """ Function to extract text from a locally downloaded PDF file

        :param pdf_path: Path of the PDF file
        :type pdf_path: `str`
        param download_papers: Whether PDF of each research paper need to be downloaded
        :type download_papers: `boolean`
        
        :return: Complete text from the research paper (includes Title, Abstract, Content etc..)
        :rtype: class `str `
    """

    if not os.path.exists(pdf_path):
        print("PDF file not Found - Exiting")
        return
    text = extract_text(pdf_path)
    if download_papers == False:
        os.remove(pdf_path)
    return text

def extract_abstract(soup):

    """ Function to extract abstract from a BS4 object

        :param soup: Soup Object with online content of the paper (not the PDF but the webpage)
        :type soup: `str`
        
        :return: Abstract of the paper
        :rtype: class `str `
    """

    return soup.find_all('p')[3:-2][0].text


def extract_authors(soup):

    """ Function to extract authors from a BS4 object

        :param soup: Soup Object with online content of the paper (not the PDF but the webpage)
        :type soup: `str`
        
        :return: Authors of the paper
        :rtype: class `list `
    """

    authors = [auth.strip() for auth in soup.find_all('p')[1].text.split(',')]
    return authors

def extract_paper_from_link(link):

    """ Function to extract Abstract, Title, Author, Year and Text details of the paper

        :param link: String version of soup Object with online content of the paper (not the PDF but the webpage)
        :type link: `str`
        
        :return: Paper_id (hash), authors, year, paper_title, pdf_name, abstract, paper_text of the research   
        :rtype: class `list `
    """

    try:

        # define global variables
        global total_papers
        global abstract_missing
        global author_missing
        global text_missing

        # Conver to BS$ element Tag
        soup = BeautifulSoup(link, 'html.parser')
        link = soup.find('a')

        # Extract Title
        paper_title = link.contents[0]

        # Get required links
        info_link = base_url + link["href"]

        # Get information from link
        blank,base_1,year,root,hash_ = link['href'].split('/')
        hash_id = hash_.split('-')[0]

        # Link for PDF of the paper
        pdf_link = base_url +'/' + base_1 + '/' + year +'/file/'+ hash_id+'-Paper.pdf'
        pdf_name = hash_id

        # Path for locally saving PDF
        pdf_path = os.path.join("working", "pdfs", str(year), pdf_name+ ".pdf")
        paper_id = pdf_name
        
        # Download PDF version of the research paper
        if not os.path.exists(pdf_path):
            pdf = requests.get(pdf_link)
            if not os.path.exists(os.path.dirname(pdf_path)):
                os.makedirs(os.path.dirname(pdf_path))
            pdf_file = open(pdf_path, "wb")
            pdf_file.write(pdf.content)
            pdf_file.close()
        
        # Extacting text from Research Paper (Includes Abstract, Title, Author etc.)
        try:
            paper_text = text_from_pdf(pdf_path, DOWNLOAD_PAPERS)
        except:
            text_missing += 1
            paper_text = ""

        html_content = requests.get(info_link).content
        paper_soup = BeautifulSoup(html_content, "html.parser")
        
        # Extracting Abstract from the webpage
        try: 
            abstract = extract_abstract(paper_soup)            
        except:
            abstract_missing += 1
            abstract = ""
        
        #Extracting Authors from the webpage
        try:
            authors = extract_authors(paper_soup)
            for author in authors:
                paper_authors.append([len(paper_authors)+1, paper_id, author[0]])       
        except:
            author_missing += 1
            authors = []

        # Increase the total paper count by 1 if extracted succeefully       
        total_papers += 1

        #Return paper details
        return [paper_id, authors, year, paper_title, pdf_name, abstract, paper_text]

    except:
        # If not successfully extracted return an empty list
        return []

if __name__ == '__main__':

    """
        Main Function
    """

    # # Global variables
    # global total_papers
    # global abstract_missing 
    # global text_missing
    # global author_missing
    
    # List of Research paper details
    papers = list()
    # List of Author details
    paper_authors = list()

    # Generate Link for Research papers of each year
    for year in range(1988,2022):
        index_urls[year] = "https://proceedings.neurips.cc/paper/%d" % (year)

    # List of no: of years
    years = [i for i in range(YEAR_MIN,YEAR_MAX)]

    # Check if the Year details are valid
    if YEAR_MIN<1988 or YEAR_MAX>2022:
        print("YEAR_MIN & YEAR_MAX should be between 1988 and 2022")
        exit()

    # Extract Papers for each year
    for year in years:

        try : 

            # Get the URL
            print("Year : ", year)
            index_url = index_urls[year]
            index_html_path = os.path.join("working", "html", str(year)+".html")

            #Download the page containing all NIPS papers for the year
            html_content = requests.get(index_url).content
            soup = BeautifulSoup(html_content, "html.parser")

            # For each paper extract all relevant details - using Multiprocessing
            paper_links = [str(link) for link in soup.find_all('a') if link["href"][:7]=="/paper/"]
            pool = mp.Pool(N_CORES)
            for d in tqdm(pool.imap(extract_paper_from_link, paper_links), total = len(paper_links)):
                papers.append(d)

        except:
            print("Connection Issue with paper of Year : ", year)


    # Create Output directory if it doesn't exist
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    # Save data as CSV
    pd.DataFrame(papers, columns=["id", "authors", "year", "title", "pdf_name", "abstract", "paper_text"]).sort_values(by="id").to_csv(os.path.join(OUTPUT_PATH, "papers.csv"), index=False, escapechar='\\')
    pd.DataFrame(paper_authors, columns=["id", "paper_id", "author_id"]).sort_values(by="id").to_csv(os.path.join(OUTPUT_PATH, "paper_authors.csv"), index=False,escapechar='\\')

    # # Print Stats
    # print("Total No of papers extracted : ", total_papers)
    # print("No of missing abstracts : ", abstract_missing )
    # print("No of missing Text : ", text_missing )
    # print("No of missing Authors : ", author_missing )
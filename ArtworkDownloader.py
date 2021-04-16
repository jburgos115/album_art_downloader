from os import walk
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
import requests
import urllib.request
import time
import re


debug = False

# # # # # DEFINITIONS # # # # #

# Objective: Extract mp3 filenames within a specified folder path and append them to a list.
# Parameters: 'path' - (String) target folder path
# Return: formatted list of songs (%author% - %title%) without file extension and replacing '&' symbol with '%26'
# NOTE: Presence of the '&' symbol in filename prevents correct SoundCloud search queries, use '%26' as it holds the
#       same value in the SoundCloud system. This will have to be reversed later when adding cover art metadata.
def get_mp3_filenames(path):
    # extracts filenames from folder with extensions
    global total_songs
    info_list = []
    for dirpath, dirnames, filenames in walk(path):
        info_list = filenames
    # removes filename extensions from each song and replaces '&' with '%26'
    for song_info in info_list:
        song_list.append(os.path.splitext(song_info.replace('&', '%26'))[0])
        total_songs += 1
    return song_list


# Objective: Generate SoundCloud search strings given a list of songs.
# Parameters: 'songs' - (String List) list of songs ==> result of 'get_mp3_filenames()'
# Return: list of SoundCloud search query urls for each song
def create_query_urls(songs):
    global total_query_urls
    query_urls = []
    for song in songs:
        "%20".join(song.split(" "))  # replace every space in 'song' with '%20'
        query_urls.append("https://soundcloud.com/search?q=" + song)
        total_query_urls += 1
    return query_urls


# Objective: Scrape SoundCloud search query urls for urls of first song result.
# Parameters: 'query_urls' - (String List) list of SoundCloud search query urls ==> result of 'create_query_urls()'
# Return: list of SoundCloud song urls
def get_first_result(query_urls):
    global total_song_urls
    scrape_progress = tqdm(total=len(query_urls), position=0, leave=True)
    song_urls = []

    for url in query_urls:
        scrape_progress.set_description("Scraping SoundCloud for song urls...")
        local_url_list = []
        response = requests.get(url)
        soup = bs(response.content, "html.parser")
        time.sleep(0.1)

        for local_url in soup.findAll('a', attrs={'href': re.compile("^/")}):
            local_url_list.append(local_url.get('href'))
        song_urls.append("https://soundcloud.com" + local_url_list[5])

        # debug: prints all local urls in SoundCloud page source
        if debug:
            print(local_url_list)

        total_song_urls += 1
        scrape_progress.update()
    scrape_progress.close()
    return song_urls


# Objective: Scrape SoundCloud song urls for artwork covers.
# Parameters: 'song_urls' - (String List) list of SoundCloud song urls ==> result of 'get_first_result()'
# Return: list of artwork urls
def get_artwork_urls(song_urls):
    download_progress = tqdm(total=len(song_urls), position=0, leave=True)
    global total_artwork_urls
    artwork_urls = []

    for song_num, url in enumerate(song_urls):
        download_progress.set_description("Scraping SoundCloud for artwork urls...")
        try:
            soup = bs(requests.get(url).content, 'html.parser')
            time.sleep(0.5)
            target_url = soup.find('img')['src']
            if target_url == '':
                print('\nSorry. There was an error getting the image url for song (' + str(song_num + 1) + ').')
                print('Possible reason: Target song exists but with no attached artwork cover.')
                print('Associated song name: ' + song_list[song_num])
                print('Associated url: ' + url + '\n')
                artwork_urls.append('Error occurred.')
                download_progress.update()
                continue
            artwork_urls.append(target_url.replace('t500x500','t3000x3000'))
            total_artwork_urls += 1
            download_progress.update()
        except Exception:
            print('\nSorry. There was an error getting the image url for song ('+str(song_num+1)+').')
            print('Possible reason: Target song does not exist with given url.')
            print('Associated song name: ' + song_list[song_num])
            print('Associated url: '+url+'\n')
            artwork_urls.append('Error occurred.')
            download_progress.update()
    download_progress.close()
    return artwork_urls


# Objective: Download artwork covers to folder destination.
# Parameters: 'artwork_urls' - (String List) list of artwork urls ==> result of 'get_artwork_urls'
#             'download_path' - (String) download destination
#             'song_filenames' - (String List) list of song filenames ==> result of 'get_mp3_filenames()'
# Return: None
def download_artwork(artwork_urls, download_path, song_filenames):
    download_progress = tqdm(total=len(artwork_urls), position=0, leave=True)
    global total_downloaded_artwork

    for song_num, url in enumerate(artwork_urls):
        download_progress.set_description("Downloading artwork...")
        if url == 'Error occurred.':
            download_progress.update()
            continue
        full_path = download_path + '\\' + song_filenames[song_num] + '.jpg'
        urllib.request.urlretrieve(url, full_path)
        total_downloaded_artwork += 1
        download_progress.update()
        time.sleep(0.5)
    download_progress.close()


# Objective: Print elements of list (newlines) to console
# Parameters: '_list' - (String List) list of Strings
# Return: None
def print_results(_list):
    print("Results: ")
    for element_index in range(len(_list)):
        print("(" + str(element_index + 1) + ")" + _list[element_index])


# Objective: Replace all instances of '%26' in mp3 filenames with '&'
# Parameters: 'song_filenames' - (String List) list of song filenames ==> result of 'get_mp3_filenames()'
# Return: None
def replace_with_ampersand(song_filenames):
    for num, song in enumerate(song_filenames):
        song_filenames[num] = song.replace('%26', '&')
    return song_filenames

# # # # # EXECUTION # # # # #

print("\n*BEWARE* This program may not correctly download artwork for songs \nthat contain non-alphanumerical characters (I'm looking at you, weebs!)\n")
print("""
-HOW TO USE-
(1) Locate the folder containing your mp3 files.
(2) Paste the folder path below.
(3) Locate/create a folder for downloading artwork.
(4) Paste download folder path when prompted to.
*Please Note* Should this program exit prematurely any and all download progress will be lost.
""")
# tracker variables
total_songs = 0
total_query_urls = 0
total_song_urls = 0
total_artwork_urls = 0
total_downloaded_artwork = 0

# Process (5-steps)
# (1) Prompt user for folder path
folder_path = input("\nEnter a folder path: ")

# (2) Get song filenames
song_list = []
song_list = get_mp3_filenames(folder_path)
print("(" + str(total_songs) + ") " + "Songs discovered in ["+folder_path+"].")
download_folder_path = input("Enter download location: ")
#print_results(song_list)

# (3) Create SoundCloud query urls
time.sleep(0.1)
print("\nCreating SoundCloud urls...")
_query_urls = create_query_urls(song_list)
print("("+str(total_query_urls)+"/"+str(total_songs)+") "+"SoundCloud query urls successfully created.\n")

# (4) Get SoundCloud song urls
time.sleep(0.1)
_song_urls = get_first_result(_query_urls)
print("("+str(total_song_urls)+"/"+str(total_songs)+") "+"Song urls successfully scraped from SoundCloud.\n")
#print_results(scraped_urls)

# (5) Get artwork urls
time.sleep(0.1)
_artwork_urls = get_artwork_urls(_song_urls)
#print_results(_artwork_urls)
print("("+str(total_artwork_urls)+"/"+str(total_songs)+") "+"Artwork urls successfully scraped from SoundCloud.\n")

# (6) Download artwork
time.sleep(0.1)
replace_with_ampersand(song_list)
download_artwork(_artwork_urls, download_folder_path, song_list)
print("("+str(total_downloaded_artwork)+"/"+str(total_songs)+") "+"Artwork successfully downloaded from SoundCloud to ["+download_folder_path+"].")
input("Press enter to continue...")
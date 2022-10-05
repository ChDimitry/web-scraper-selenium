from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import PySimpleGUI as sg
import datetime
import guiLayout
import threading
import paths
import time
import re

PATH = "C:\Program Files (x86)\chromedriver.exe"
URL = "https://www.google.com/"

#--------------------------------------------------------------------------------------------------------#
# Gets an element and waits until it's fully loaded
def objectLoad(path):
    return WebDriverWait(driver, 10).until(EC.element_to_be_clickable(path))

# Logs the time, action and comment of an event
def logIt(action, comment):
    logger.write("%s %s %s \n" % (datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), action, comment))

# Splits the text into lines, then splits the lines into words and checks if key is one of those words
# Converts all words that are key into uppercase and then join everything back together
def stringFilter(text, key):
    capital_key = key.capitalize()
    splitted_text = text.split("\n")
    output = ""
    seperators = r"[\' \"]+"
    for line in splitted_text:
        if len(line) > 200 and line[0] != "^" and not line[0].isdigit() and line[0].isupper():
            # Split the lines on all spaces, apostrophes and quotation marks
            splitted_line = re.split(seperators, line)
            if key in splitted_line or capital_key in splitted_line:
                # figure out the list-indices of occurences of the key word
                idxs = [i for i, x in enumerate(splitted_line) if (x == key or x == capital_key)]
                # modify the occurences by uppercasing them
                for i in idxs:
                    splitted_line[i] = splitted_line[i].upper()
            splitted_line = " ".join(splitted_line)
            output += splitted_line + "\n\n"
    return output

# Use the webdriver to initilialize and open the Chrome browser
def chromeInit():
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver.get(URL)

# Removes illegal chars from the string
def fixString(str):
    #define special characters list
    special_characters = ['|', '/', '?', '*', '<', '>', ':', '"']
    str = ''.join(filter(lambda i:i not in special_characters, str))
    return str

# Returns the amount of time key appeard in text
def countKeyword(key, text):
    return text.count(key.upper())

#------------------------------------------------------------------------------------#
logger = open("log.txt", mode='a', encoding='utf-8')
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path=PATH, options=options)
init_thread = threading.Thread(target=chromeInit)
init_thread.start()
window = sg.Window("Keyword Scrapper", guiLayout.layout, finalize=True, size=(1100, 500))

while True:
    event, values = window.read()
    if event == "Search":
        title_list = ""
        href_list = ""
        search_input = values["-SEARCH-"]
        if len(search_input) == 0:
            # Trying to search nothing lol
            sg.popup_auto_close("\nSearch bar is empty\n", keep_on_top=True, no_titlebar=True, button_type=5)
        else:
            # Check if the current loaded page is Google's main search pageS
            if objectLoad((By.NAME, "q")) == None:
                objectLoad((By.CLASS_NAME, "gLFyf gsfi")).clear()
                objectLoad((By.CLASS_NAME, "gLFyf gsfi")).send_keys(search_input + Keys.ENTER)
            else:
                objectLoad((By.NAME, "q")).clear()
                objectLoad((By.NAME, "q")).send_keys(search_input + Keys.ENTER)
            
            # Collect titles and their address
            objectLoad((By.XPATH, paths.href_XPATH))
            search_result_href = driver.find_elements(By.XPATH, paths.href_XPATH)
            more_results = driver.find_elements(By.XPATH, "//div[@jsname='Cpkphb']")
            for result in more_results:
                # "People also ask" section, open them up one by one    
                time.sleep(0.4)
                try:
                    result.click()
                except:
                    # Not very often, but sometimes it won't click on one of the 'Cpkphb' titlesS
                    # This is a known bug, don't know how to fix it yet
                    continue
            search_result_title = driver.find_elements(By.XPATH, paths.header_XPATH)
            
            # List of addresses
            href_list = [
                href.get_attribute("href")
                for href in search_result_href
            ]

            # List of titles
            title_list = [
                fixString(title.text)
                for title in search_result_title
                if len(title.text) != 0
            ]
            if len(href_list) != len(title_list):
                event = "Search"

            # Print the titles inside the listbox and update the search status
            window["-METRICS-"].update(
                "The seach for '%s' yielded %s results." % (search_input, len(title_list))
            )
            window["-TITLE-"].update(title_list)

    # If the user chose one of the output titles
    if event == "-TITLE-" and len(title_list) > 0 and len(search_input) != 0:
        title = values["-TITLE-"][0]
        try:
            # Check if a user previously saved this info in a file
            saved_header_file = open("%s.txt" % title, mode='r', encoding='utf-8')
            info = stringFilter(saved_header_file.read(), search_input)
        except:
            # If the file doesn't exist, pull new info from the page
            index = title_list.index(title)
            driver.get(href_list[index])
            body = objectLoad((By.TAG_NAME, "body")).text
            info = stringFilter(body, search_input)

        window["-METRICS-"].update("'%s' contains the keyword '%s' %d times." % (title, search_input, countKeyword(search_input, info)))
        window["-INFO-"].update(info)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    if event == "Version":
        if event == 'Version':
            sg.popup("Versions", sg.get_versions(), keep_on_top=True, no_titlebar=False)
    
    if event == "Clear":
        window["-SEARCH-"].update('')
        window["-TITLE-"].update('')
        window["-INFO-"].update('')
        window["-METRICS-"].update('')
        title_list.clear()
        href_list.clear()

    if event == "Save Result":
        if len(title_list) > 0 and len(title) > 0:
            save_info = open("%s.txt" % title, mode='a', encoding='utf-8')
            save_info.write(info)
            save_info.close()
        else:
            sg.popup_auto_close("\nNo Results\n", keep_on_top=True, no_titlebar=True, button_type=5)

logger.close()
window.close()
driver.close()
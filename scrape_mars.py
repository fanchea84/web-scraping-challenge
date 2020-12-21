########################################################################################################################################
# Purpose of SCRAPE_MARS.PY is to scrape 3 websites for information related to planet Mars
# How: leverage MongoDB with Flask templating 
########################################################################################################################################

# Import Dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import requests
import pprint


# Scrape function to return Python dictionary
def scrape():
    # This step opens a new chrome window that will be driven by code in the next few cells
    # It also adds another Chrome icon on the taskbar because it's using chromedriver instead of chrome
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    # define blank mars dictionary
    mars_dict = {}
    # call each "sub" function
    mars_dict["mars_headline"] = mars_news_function(browser)
    mars_dict["jpl_mars_image"] = jpl_image_function(browser)
    mars_dict["mars_facts_table"] = mars_facts_function(browser)
    mars_dict["mars_hemisphere_images"] = mars_hemisphere_function(browser)
    print(mars_dict)
    # Close the chromebrowser window
    browser.quit()
    return mars_dict


############################################################################################################################
# NASA Mars News: Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text.
############################################################################################################################
# This step creates a function MARS_NEWS_FUNCTION that navigates the chromebrowser window to NASA News site & runs BeautifulSoup to parse the site's HTML
def mars_news_function(browser):
    nasa_url = "https://mars.nasa.gov/news/"
    browser.visit(nasa_url)
    sleep(3)  # This is a manual delay that prevents a "Race Condition" with JavaScript and this script competing for resources
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    # Grab the latest headline from NASA Mars News
    nasa_headline = soup.find_all("div", class_="content_title")[0].get_text()
    return nasa_headline


############################################################################################################################
# JPL Mars Space Images: Use splinter to find the current Featured Mars Image
############################################################################################################################
# This step creates a function JPL_IMAGE_FUNCTION that navigates the chromebrowser window to JPL images site & runs BeautifulSoup to parse the site's HTML
def jpl_image_function(browser):
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    sleep(3)  # This is a manual delay that prevents a "Race Condition" with JavaScript and this script competing for resources
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    # This step clicks on the FULL IMAGE link (in the chromebrowser window)
    browser.click_link_by_partial_text("FULL IMAGE")
    # browser.links.find_by_partial_text("FULL IMAGE")
    # This step clicks on the MORE INFO link (in the chromebrowser window)
    sleep(3)  # This is a manual delay that prevents a "Race Condition" with JavaScript and this script competing for resources
    browser.click_link_by_partial_text("more info")
    # browser.links.find_by_partial_text("more info")
    # This step clicks on the JPEG image (in the chromebrowser window)
    browser.click_link_by_partial_text(".jpg")
    # This step saves as a variable the URL of the JPEG image file
    featured_image_url = browser.url
    return featured_image_url


############################################################################################################################
# Mars Facts: Use Pandas to scrape the Mars Data table containing facts about the planet including Diameter, Mass, etc.
############################################################################################################################
def mars_facts_function(browser):
    # Define URL of Mars Facts website
    facts_url = "https://space-facts.com/mars/"
    #  Read in data table via Pandas.
    # Specify zero'th position to get just Mars data, since table contains both Mars & Earth data
    facts_df = pd.read_html(facts_url)[0]
    # Create a "pretty" Mars Facts dataframe with column headers and text clean-up
    facts_df.columns = ["Metric", "Value (Planet Mars)"]
    # Remove the colon character in DESCRIPTION column
    facts_df["Metric"] = facts_df["Metric"].str.replace(":", "")
    facts_df
    # Use Pandas to convert the data to a HTML table string
    facts_df.set_index("Metric", inplace=True)
    facts_html = facts_df.to_html()
    return facts_html


###################################################################################################################################
# Mars Hemispheres: Scrape from USGS Astrogeology site hi-res images for each of Mars' hemispheres, including URL for each image.
###################################################################################################################################
def mars_hemisphere_function(browser):
    # This step navigates the chromebrowser window to USGS Astrogeology & runs BeautifulSoup to parse the site's HTML
    mars_hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(mars_hemisphere_url)
    sleep(3)  # This is a manual delay that prevents a "Race Condition" with JavaScript and this script competing for resources
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    # Create list of Mars Hemisphere names, empty list for housing hemisphere image URLs,
    # and empty dictionary for housing hemisphere names & image URLS
    mars_hemispheres = ["Cerberus", "Schiaparelli", "Syrtis", "Valles"]
    hemisphere_pic_urls = []
    hemi_dict = {}
    # Loop through list of hemispheres, and populate dictionary with name & image URL by scraping USGS site
    for hemi in mars_hemispheres:
        browser.click_link_by_partial_text(hemi)
        hemi_html = browser.html
        soup = BeautifulSoup(hemi_html, 'html.parser')
        hemi_dict["title"] = soup.find(
            "h2").get_text().replace("Enhanced", "").strip()
        hemi_dict["img_url"] = soup.find_all("div", class_="downloads")[
            0].find_all("a")[0]["href"]
        hemisphere_pic_urls.append(hemi_dict)
        browser.back()  # go back to original page with all the hemispheres
    # Print dictionary containing Mars hemisphere names & images
    return hemisphere_pic_urls



if __name__ == "__main__":
    # Use to test as stand-alone script, decoupled from Flask app
    scrape() # call SCRAPE function
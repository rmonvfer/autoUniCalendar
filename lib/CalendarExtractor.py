# Copyright Ramón Vila Ferreres - 2021

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import requests
import pprint as pp
import logging
from urllib.parse import urlencode

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

logging.basicConfig(format= '%(name)s - %(levelname)s - %(message)s', level= logging.INFO)
logger = logging.getLogger("CalendarExtractor")

class CalendarExtractor:
    """ Requests and extracts raw calendar data straight from SIES """

    def __init__(self, configuration, username, password):
        self.configuration = configuration
        self.credentials = { "username": username, "password": password } 

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")

        self.driver= webdriver.Chrome(
            executable_path=self.configuration["params"]["CHROMEDRIVER_PATH"],
            chrome_options=self.options)

        self.wait = WebDriverWait(self.driver, 20)
        self.cookies = self.__extract_user_cookies()

    def __get_element(self, xpath, clickable= False):
        if clickable:
            # Wait until the element becomes clickable
            return self.wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        else:
            # Wait until the element exists
            return self.wait.until(ec.presence_of_element_located((By.XPATH, xpath)))

    def __click(self, xpath):
        self.__get_element(xpath, clickable=True).click()

    def __extract_user_cookies(self):
        """ Dumps user cookies using Selenium Chromedriver (headless mode) """

        self.driver.get(self.configuration["params"]["LOGIN_URL"])

        # Username
        username_textarea = self.__get_element(self.configuration["xpaths"]["username_input"])
        username_textarea.clear()
        username_textarea.send_keys(self.credentials["username"])

        # Password
        password_textarea = self.__get_element(self.configuration["xpaths"]["password_input"])
        password_textarea.clear()
        password_textarea.send_keys(self.credentials["password"])

        # Submit the form
        self.__click(self.configuration["xpaths"]["login_button"])
        
        user_cookies =  { 
            'JSESSIONID': self.driver.get_cookie("JSESSIONID")["value"], 
            'oam.Flash.RENDERMAP.TOKEN': self.driver.get_cookie("oam.Flash.RENDERMAP.TOKEN")["value"]
        }

        logger.info("Got user cookies!")
        self.driver.close()

        return user_cookies

    def __get_calendar_source(self):
        """ Extract calendar's page raw HTML """

        logger.info("Requesting calendar source using dumped cookies")

        # Actually perform the request
        request = requests.get( self.configuration["params"]["BASE_CALENDAR_URL"], cookies= self.cookies )
        self.calendar_page_source = request.text

        logger.info("Calendar HTML succesfully dumped")


    def __extract_state_parameters(self):
        """ Parse the dumped raw HTML to extract state parameters """

        logger.info("Extracting state parameters")
        page_soup = BeautifulSoup(self.calendar_page_source, "html.parser")
        
        # Find the submit form
        javax_form = page_soup.select('form[action="/serviciosacademicos/web/expedientes/calendario.xhtml"]')[0]
        
        # Extract form parameters and attbs
        javax_faces_form   = page_soup.find("div", {"class": "card-body"})
        javax_faces_source = javax_faces_form.find("div")
        javax_faces_source_submit, javax_faces_viewstate = javax_form.find_all("input")

        self.state = {
            "javax.faces.source": javax_faces_source["id"],
            "javax.faces.source_SUBMIT": javax_faces_source_submit["name"],
            "javax.faces.viewstate": javax_faces_viewstate["value"]
        }
        logger.info("State parameters extracted")
        

    def __request_calendar_events(self):
        """ Requests the calendar data to UniOvi servers """

        payload= urlencode({ 
            # JSF state parameters
            "javax.faces.source":          self.state["javax.faces.source"],
            "javax.faces.partial.execute": self.state["javax.faces.source"],
            "javax.faces.partial.render":  self.state["javax.faces.source"],
            "javax.faces.ViewState":       self.state["javax.faces.viewstate"],

            # TODO: More reversing needed here! (why is this mandatory?)
            self.state["javax.faces.source"]: self.state["javax.faces.source"],

            # TODO: refactor this to make it user-adjustable
            # Start and end times are just Unix timestamps (adjusted to GMT +2)
            self.state["javax.faces.source"] + "_start": "1630886400000",
            self.state["javax.faces.source"] + "_end":   "1652054400000",
            
            # Form-related parameters
            self.state["javax.faces.source_SUBMIT"]: 1,
            "javax.faces.partial.ajax": "true"
        })

        logger.info("Requesting calendar events to SIES server")

        r = requests.post(
            self.configuration["params"]["BASE_CALENDAR_URL"], 
            data= payload,
            headers= { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' }, 
            cookies= self.cookies
        )
        logger.info("Successfuly dumped calendar data")
        return r.text


    def get_calendar_data(self):
        """ Logs into sies.uniovi.es and dumps the (raw) user calendar """

        self.__get_calendar_source()
        self.__extract_state_parameters()

        return self.__request_calendar_events()

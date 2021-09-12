# Copyright Ramón Vila Ferreres - 2021

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from lib.model.CalendarEvent import CalendarEvent
import re
import json
import pprint as pp
from datetime import datetime
import io
import csv
from typing import *
import logging

logging.basicConfig(format= '%(name)s - %(levelname)s - %(message)s', level= logging.INFO)
logger = logging.getLogger("CalendarParser")

class CalendarParser:
    """ Parses raw calendar data (JSF <response></response> ) into several formats """

    def __init__(self, configuration: dict, raw_partial_response: str):
        self.configuration = configuration
        self.response_raw  = raw_partial_response
        self.response_json   : str  = re.search(":\s(\[(.|\s)*?\])", self.response_raw).group(1).replace("\n", "").strip()
        self.response_parsed : dict = json.loads(self.response_json)

    def as_json(self) -> str:
        """ Returns the calendar reprsentation in JSON format"""
        return self.response_parsed
    
    def as_csv(self) -> str:
        """ Returns the calendar representation using Google Calendar's CSV format """
        csv_content = []
        output: io.StringIO = io.StringIO()
        writer: csv.writer = csv.writer(output, quoting=csv.QUOTE_NONE)

        # Read headers and split them 
        csv_headers: List[str] = self.configuration["parser"]["formats"]["csv"]["headers"].split(",")

        # Add quotes to the last item (as it is the event's description)
        csv_headers[-1] = f"{csv_headers[-1]}"
        csv_content.append(csv_headers)

        # Iterate over all items in the calendar and parse them into a list
        for event_data in self.response_parsed:
            event = CalendarEvent(self.configuration, event_data)
            csv_content.append(event.to_list())
        
        # Count all the processed events
        self.processed_events = len(csv_content) -1

        # Write everything
        writer.writerows(csv_content)

        # Return the string version
        return output.getvalue()
# Copyright Ramón Vila Ferreres - 2021

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from typing import *
import dateutil.parser
from datetime import datetime

class CalendarEvent:
    """ Represents a single calendar event in several formats """

    def __init__(self, configuration: dict, event: dict):
        # Here for ease of access and readability
        event_start = self.__parse_datestring(event["start"])
        event_end   = self.__parse_datestring(event["end"])

        self.configuration = configuration

        # Parse data
        self.event: dict = {
            "description": event["description"].replace("\n", ""),
            "subject"    : event['title'].replace("\n", ""),
            "start_date" : event_start.strftime("%m/%d/%Y"),
            "start_time" : event_start.strftime("%H:%M:%S"),
            "end_date"   : event_end.strftime("%m/%d/%Y"),
            "end_time"   : event_end.strftime("%H:%M:%S"),
        }
    
    def __parse_datestring(self, datestring: str) -> datetime:
        return dateutil.parser.isoparse(datestring)
    
    def to_list(self) -> List[Any]:
        """ Returns event components sorted in an array """
        csv_headers = self.configuration["parser"]["formats"]["csv"]["headers"].split(",")

        # Replace the value in its original position to follow the specification order
        values: dict = { key : self.event[key.lower().replace(" ", "_")] for key in csv_headers }

        return list(values.values())
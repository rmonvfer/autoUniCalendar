# Copyright Ramón Vila Ferreres - 2021

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import re
import json

class CalendarParser:

    def __init__(self, raw_partial_response):
        self.response_raw    = raw_partial_response
        self.response_json   = re.search(":\s(\[(.|\s)*?\])", self.response_raw).group(1).replace("\n", "").strip()
        self.response_parsed = json.loads(self.response_json)

    def as_json(self):
        return self.response_parsed

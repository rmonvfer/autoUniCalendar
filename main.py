# Copyright Ramón Vila Ferreres - 2021
# Forked from https://github.com/Bimo99B9/autoUniCalendar

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from lib.CalendarExtractor import CalendarExtractor
import json, getpass

user_settings = {}

def main():
    username = str(input("[#] Username > "))
    password = getpass.getpass(prompt="[#] Password > ")

    # Read user settings
    with open("settings.json", "r", encoding="utf-8") as settings_file:
        user_settings = json.load(settings_file)
    
    # Instantiate the extractor
    extractor = CalendarExtractor(user_settings, username, password)
    calendar_data = extractor.get_calendar_data()

    with open("raw.txt", "w+", encoding="utf-8") as fp:
        fp.write(calendar_data)
    
if __name__ == "__main__":
    main()
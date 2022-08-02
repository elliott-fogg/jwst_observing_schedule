import requests
from bs4 import BeautifulSoup as BS
import re
import os
import pandas as pd

# Get the HTML code for the website
r1 = requests.get("https://www.stsci.edu/jwst/science-execution/observing-schedules")

# If request was unsuccessful, abort
if r1.status_code != 200:
    print("Reading page was unsuccessful!")
    print(f"Status Code: {r1.status_code}")
    print(f"Reason: {r1.reason}")

# Convert the HTML of the website to 'soup' to be searched
soup = BS(r1.text)

# Extract all hyperlinks from the soup
hyperlinks = soup.find_all("a")

# Extract urls from hyperlinks
urls = [a["href"] for a in hyperlinks]

# Restrict to urls that contain "science-execution/observing-schedules/_documents",
# as this was determined to be unique to the files we're after.
# Also extract the YYYYMMDD-format date for each file.
filepaths = [(url, re.findall('_report_(\d{8}).txt', url)) for url in urls]

# Sort to find latest file
latest_filepath = sorted(filepaths, key=lambda x: x[1], reverse=True)[0][0]

# Request file
r2 = requests.get("https://www.stsci.edu/" + latest_filepath)

# If request was unsuccessful, abort
if r2.status_code != 200:
    print("Obtaining file was unsuccessful!")
    print(f"Status Code: {r2.status_code}")
    print(f"Reason: {r2.reason}")

# Split downloaded file into lines
lines = r2.text.split("\n")

# Establish the Regular Expression we'll be using to extract each line
pattern = '^(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)[ ]{2,}(.+?)$'

# Extract the headings as an array
headings = re.findall(pattern, lines[2])[0]

# Extract all entries
entries = []
for i in range(4, len(lines)):
    current = lines[i]
    matches = re.findall(pattern, current)
    if len(matches) > 0:
        entries.append(matches[0])

# Create a Pandas DataFrame from the results, and save to disk
output_filename = "latest_jwst_observations.csv"
df = pd.DataFrame(entries, columns=headings)
df.to_csv(output_filename, index=False)

print(os.getcwd())
print(f"File downloaded. Saved as '{os.path.join(os.getcwd(), output_filename)}')")
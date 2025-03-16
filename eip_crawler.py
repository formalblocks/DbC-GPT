import requests
from bs4 import BeautifulSoup
import html2text

# Fetch the EIP page content
url = "https://eips.ethereum.org/EIPS/eip-3156"
response = requests.get(url)
html_content = response.text

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Extract the main content (adjust the selector as needed)
main_content = soup.find('div', class_='main')
if main_content:
    html_content = str(main_content)
else:
    # If specific main content selector fails, use the whole body
    body = soup.find('body')
    html_content = str(body)

# Convert HTML to Markdown
converter = html2text.HTML2Text()
converter.ignore_links = False
converter.ignore_images = False
converter.body_width = 0  # Don't wrap text
markdown_content = converter.handle(html_content)

# Save to file
with open('eip-3156.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("Conversion complete! Saved to eip-3156.md")
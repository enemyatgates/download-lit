import optimise
import os
import re
import sys
import json
import requests
import logging
import inspect
import shutil
from alive_progress import alive_bar
from datetime import datetime

"""Configure Logging"""
logging.basicConfig(filename = 'script.log', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

"""Extracts the Story Identifier from the given Literotica URL."""
def init_link_to_link_base(input_url):
	match = re.search(r'/\w/(.+)', input_url)
	if match:
		return match.group(1)
	else:
		logging.error("Invalid URL Format : %s", input_url)
		raise ValueError("Invalid Literotica URL Format")

"""Constructs the API Request URL."""
def link_base_to_link(link_base, page_number):
	return f'https://literotica.com/api/3/stories/{link_base}?params=%7B"contentPage"%3A{page_number}%7D'

"""Fetches JSON Data from the given API Link."""
def get_json(link):
	headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'}
	try:
		response = requests.get(link, headers = headers, timeout = 10)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		logging.error("Request Failed: %s", type(e).__name__, e)
		return None

"""Creates a Unique Output Filename."""
def create_output(path_output, erotica_url):
	suffix = 0
	file_output = os.path.join(path_output, f"erotica_{erotica_url}_{suffix}.md")
	while os.path.exists(file_output):
		suffix += 1
		file_output = os.path.join(path_output, f"erotica_{erotica_url}_{suffix}.md")
	return file_output

"""Generates Content Header and Footer."""
def get_headerfooter():
	content_header = f'<style> @import "https://enemyatgates.github.io/hosting/CG%2BJOPLINSTYLEUSER_%7B00%7D.css" </style>\n'
	content_header += f'* * *\n'
	content_header += f'${{toc}}\n'
	content_header += f'* * *\n'
	content_header += f'#### The Beginning\n'
	content_header += f'* * *\n'
	content_footer = f"* * *\n"
	content_footer += f"#### The End\n"
	content_footer += f"#### Attributes\n"
	content_footer += f"| Date Compile | {datetime.now().isoformat()} |\n"
	content_footer += f"| - | - |\n"
	content_footer += f"| Compiler | [Compiler](CompilerUrl) |\n"
	content_footer += f"* * *\n"
	return content_header, content_footer

"""Fetches and Saves a Story's content to a File."""
def get_story(link_base, file_output):
	content_json = get_json(link_base_to_link(link_base, 1))
	if not content_json:
		logging.error("Failed to fetch initial JSON for %s", link_base)
		return
	story_pages = content_json.get('meta', {}).get('pages_count', 1)
	story_title = content_json.get('submission', {}).get('title', 'Unknown Title')
	story_author = content_json.get('submission', {}).get('authorname', 'Unknown Author').lower()
	story_category = content_json.get('submission', {}).get('category_info').get('pageUrl')
	story_description = content_json.get('submission', {}).get('description', 'Unknown')
	story_datetime = datetime.strptime(content_json.get('submission', {}).get('date_approve'), "%m/%d/%Y").isoformat()
	story_tags = [tag['tag'] for tag in content_json.get('submission', {}).get('tags', [])]
	story_link = f'https://literotica.com/s/{link_base}'
	story_header_main = f"\n* * *\n"
	story_header_main += f"##### {story_title}\n"
	story_header_main += f"| Title | {story_title} |\n"
	story_header_main += f"| - | - |\n"
	story_header_main += f"| Author | {story_author} |\n"
	story_header_main += f"| Source | {story_link} |\n"
	story_header_main += f"| Category | {story_category} |\n"
	story_header_main += f"| Description | {story_description} |\n"
	story_header_main += f"| Date Publish | {story_datetime}|\n"
	story_header_main += f"| Tags | {story_tags} |\n"
	story_header_main += f"* * *\n"
	print(story_header_main)
	with open(file_output, 'a', encoding = 'utf-8') as file:
		file.write(story_header_main)
	with alive_bar(story_pages) as bar:
		for i in range(1, story_pages + 1):
			story_header_page = f"\n* * *\n###### Page {str(i).zfill(2)}\n* * *\n"
			story_page = get_json(link_base_to_link(link_base, i))
			story_text = story_page.get('pageText', 'Content Not Available') if story_page else 'Error Fetching Page.'
			with open(file_output, 'a', encoding = 'utf-8') as file:
				file.write(story_header_page)
				file.write(story_text)
			bar()

"""Handles Fetching either an Entire Series or a Single Story."""
def get_series(link_base, path_output):
	content_header, content_footer = get_headerfooter()
	content_json = get_json(link_base_to_link(link_base, 1))
	if not content_json:
		logging.error("Failed to Fetch JSON for %s", link_base)
		return None
	try:
		series_data = content_json.get('submission', {}).get('series', {})
		erotica_url = series_data.get('meta', {}).get('url', link_base)
		erotica_items = series_data.get('items', [content_json.get('submission', {})])
		file_output = create_output(path_output, erotica_url)
		for item in erotica_items:
			get_story(item.get('url', link_base), file_output)
	except AttributeError:
		erotica_url = content_json.get('submission', {}).get('url', link_base)
		erotica_items = erotica_url
		file_output = create_output(path_output, erotica_url)
		get_story(erotica_items, file_output)
	except Exception as e:
		logging.error("Unexpected Error: %s", type(e).__name__, e)
		return None
	return file_output

"""Function Main"""
if (__name__ == '__main__'):
	if len(sys.argv) < 2:
		print(f"Usage: python main.py <Literotica Story URL>")
		sys.exit(1)
	input_url = sys.argv[1].strip()
	path_output = sys.argv[2].strip() if len(sys.argv) > 2 else "fucker"
	os.makedirs(path_output, exist_ok = True)
	print("≈" * shutil.get_terminal_size().columns)
	print(f"Downloading Erotica:\n\tWeb Link:\t{input_url}\n\tLocation:\t{path_output}")
	print("≈" * shutil.get_terminal_size().columns)
	try:
		link_base = init_link_to_link_base(input_url)
		erotica_file = get_series(link_base, path_output)
		content_header, content_footer = get_headerfooter()
		if erotica_file:
			with open(erotica_file, "r+", encoding="utf-8") as file:
				erotica_content = file.read().strip()
				erotica_content = optimise.process_content(f"{content_header}\n{erotica_content}\n{content_footer}")
				file.seek(0)
				file.write(erotica_content)
				file.truncate()
			print(f"File Erotica Generation Succeeded: {erotica_file}")
		else:
			print("File Erotica Generation Failed. Check script.log for details.")
	except Exception as e:
		logging.error("Critical Failure: %s", type(e).__name__, e)
		print("Error Occurred. Check script.log for details.")
	print("≈" * shutil.get_terminal_size().columns)

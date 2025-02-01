import os
import re
import sys
import json
import requests
import logging
from alive_progress import alive_bar

"""Configure Logging"""
logging.basicConfig(filename = 'script.log', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

"""Extracts the Story Identifier from the given Literotica URL."""
def init_link_to_link_base(init_link):
	match = re.search(r'/\w/(.+)', init_link)
	if match:
		return match.group(1)
	else:
		logging.error("Invalid URL Format : %s", init_link)
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

"""Fetches and Saves a Story's content to a File."""
def get_story(link_base, output_file):
	init_json = get_json(link_base_to_link(link_base, 1))
	if not init_json:
		logging.error("Failed to fetch initial JSON for %s", link_base)
		return
	pages_count = init_json.get('meta', {}).get('pages_count', 1)
	title = init_json.get('submission', {}).get('title', 'Unknown Title')
	author_name = init_json.get('submission', {}).get('authorname', 'Unknown Author')
	author_homepage = init_json.get('submission', {}).get('author', {}).get('homepage', 'Unknown Author  Homepage')
	story_link = f'https://literotica.com/s/{link_base}'
	title_with_border = f"\n* * *\n| Title | {title} |\n| - | - |\n| Author | {author_name} |\n| Author | {author_homepage} |\n| Source | {story_link} |\n* * *\n"
	with open(output_file, 'a', encoding = 'utf-8') as file:
		file.write(title_with_border)
	with alive_bar(pages_count) as bar:
		for i in range(1, pages_count + 1):
			page_number_with_border = f"\n* * *\n| Page | {str(i).zfill(2)} |\n* * *\n"
			story_page = get_json(link_base_to_link(link_base, i))
			story_text = story_page.get('pageText', 'Content Not Available') if story_page else 'Error Fetching Page.'
			with open(output_file, 'a', encoding = 'utf-8') as file:
				file.write(page_number_with_border)
				file.write(story_text)
			bar()

"""Creates a Unique Output Filename."""
def create_output(output_dir, erotica_url):
	suffix = 0
	output_file = os.path.join(output_dir, f"erotica_{erotica_url}_{suffix}.txt")
	while os.path.exists(output_file):
		suffix += 1
		output_file = os.path.join(output_dir, f"erotica_{erotica_url}_{suffix}.txt")
	return output_file

"""Handles Fetching either an Entire Series or a Single Story."""
def get_series(link_base, output_dir):
	init_json = get_json(link_base_to_link(link_base, 1))
	if not init_json:
		logging.error("Failed to Fetch JSON for %s", link_base)
		return None
	try:
		series_data = init_json.get('submission', {}).get('series', {})
		erotica_url = series_data.get('meta', {}).get('url', link_base)
		erotica_items = series_data.get('items', [init_json.get('submission', {})])
		output_file = create_output(output_dir, erotica_url)
		for item in erotica_items:
			get_story(item.get('url', link_base), output_file)
	except AttributeError:
		erotica_url = init_json.get('submission', {}).get('url', link_base)
		erotica_items = erotica_url
		output_file = create_output(output_dir, erotica_url)
		get_story(erotica_items, output_file)
	except Exception as e:
		logging.error("Unexpected Error: %s", type(e).__name__, e)
		return None
	return output_file

"""Function Main"""
if (__name__ == '__main__'):
	if len(sys.argv) < 2:
		print(f"Usage: python main.py <Literotica Story URL>")
		sys.exit(1)
	input_url = sys.argv[1]
	output_dir = sys.argv[2] if len(sys.argv) > 2 else "downloads_erotica"
	os.makedirs(output_dir, exist_ok = True)
	print(f"Downloading Erotica: {input_url} to {output_dir}")
	try:
		link_base = init_link_to_link_base(input_url)
		erotica_file = get_series(link_base, output_dir)
		if erotica_file:
			print(f"File Erotica Generation Succeeded: {erotica_file}")
		else:
			print("File Erotica Generation Failed. Check script.log for details.")
	except Exception as e:
		logging.error("Critical Failure: %s", type(e).__name__, e)
		print("Error Occurred. Check script.log for details.")

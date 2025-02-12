import argparse
import os
import re
def process_content(content):
	replacements = {'“': '"', '”': '"', '‘': "'", '’': "'", '–': '-', '—': '-', '‒': '-', '―': '-', '−': '-'}
	while True:
		content_original = content
		for old, new in replacements.items(): content = content.replace(old, new)
		content = re.sub(r'\r\n', '\n', content)
		content = re.sub(r'\r', '\n', content)
		content = re.sub(r'\n{3,}', '\n\n', content)
		content = re.sub(r'[ ]{2,}', ' ', content)
		content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
		content = re.sub(r'^[ ]+', '', content, flags=re.MULTILINE)
		content = re.sub(r'^([\*]+)$', '* * *', content, flags=re.MULTILINE)
		content = re.sub(r'^([-]+)$', '* * *', content, flags=re.MULTILINE)
		content = re.sub(r'^([_]+)$', '* * *', content, flags=re.MULTILINE)
		content = re.sub(r'^([=]+)$', '* * *', content, flags=re.MULTILINE)
		content = re.sub(r'^([+]+)$', '* * *', content, flags=re.MULTILINE)
		content = re.sub(r'\* \* \*\n\* \* \*', '* * *', content)
		content = re.sub(r'\n\n\|', '\n|', content)
		content = re.sub(r'\n\n\*', '\n*', content)
		content = re.sub(r'\*\n\n', '*\n', content)
		if content == content_original:
			break
	return content
def process_file(file_input, file_output, file_header, file_footer):
	with open(file_header, 'r', encoding='utf-8') as file: content_header = file.read().strip()
	with open(file_footer, 'r', encoding='utf-8') as file: content_footer = file.read().strip()
	with open(file_input, 'r', encoding='utf-8') as file: content_input = file.read().strip()
	with open(file_output, 'w', encoding='utf-8') as file:
		file.write(process_content(f"{content_header}\n{content_input}\n{content_footer}"))
	print(f"Processed:\t{file_input}\nSaved As:\t{file_output}\n", "="*113)
def process_directory(path_input, path_output, file_header, file_footer, file_extensions):
	counter = 0
	for root, _, files in os.walk(path_input):
		for file in files:
			if any(file.endswith(extension) for extension in file_extensions):
				print(str(counter).rjust(4, "0"))
				file_input = os.path.join(root, file)
				path_update = os.path.join(path_output, os.path.relpath(root, path_input)) if not os.path.relpath(root, path_input) == "." else path_output
				os.makedirs(path_update, exist_ok=True)
				file_output = os.path.join(path_update, file)
				process_file(file_input, file_output, file_header, file_footer)
				counter += 1
	print(f"Processed:\n\tFile Count:\t{str(counter).rjust(4, "0")}\n\tFile Ext:\t{file_extensions}\n\tPath Input:\t{path_input}\n\tPath Output:\t{path_output}\n")
if (__name__ == '__main__'):
	parser = argparse.ArgumentParser(description='Optimise Files and Insert Header and Footer.')
	parser.add_argument('-pi', '--path_input', required=True, type=str, help='Path to the Directory Input')
	parser.add_argument('-po', '--path_output', required=True, type=str, help='Path to the Directory Output')
	parser.add_argument('-fh', '--file_header', required=True, type=str, help='Path to the File Header')
	parser.add_argument('-ff', '--file_footer', required=True, type=str, help='Path to the File Footer')
	parser.add_argument('-fe', '--file_extension', required=False, help='File Extensions', nargs='+', default=[".md", ".txt"])
	args = parser.parse_args()
	if not os.path.isdir(args.path_input): raise Exception(f"Invalid Directory Input: '{os.path.normpath(args.path_input)}'.")
	if not os.path.isdir(args.path_output): raise Exception(f"Invalid Directory Output: '{os.path.normpath(args.path_output)}'.")
	if not os.path.isfile(args.file_header): raise Exception(f"Invalid File Header: '{os.path.normpath(args.file_header)}'.")
	if not os.path.isfile(args.file_footer): raise Exception(f"Invalid File Footer: '{os.path.normpath(args.file_footer)}'.")
	if (args.path_output == args.path_input): raise Exception(f"{os.path.normpath(args.path_input)} and {os.path.normpath(args.path_output)} are same.")
	if (os.path.commonpath([args.path_input]) == os.path.commonpath([args.path_input, args.path_output])): raise Exception(f"{os.path.normpath(args.path_input)} is parent of {os.path.normpath(args.path_output)}.")
	process_directory(os.path.normpath(args.path_input), os.path.normpath(args.path_output), os.path.normpath(args.file_header), os.path.normpath(args.file_footer), args.file_extension)

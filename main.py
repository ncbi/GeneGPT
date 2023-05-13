__author__ = 'qiao'

'''
teach LLMs to use NCBI API
'''

import json
import openai
openai.api_key = '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'
import os
import urllib.parse
import urllib.request
import requests
import re
import time
import sys

def call_api(url):
	time.sleep(1)
	url = url.replace(' ', '+')
	print(url)

	req = urllib.request.Request(url) 
	with urllib.request.urlopen(req) as response:
		call = response.read()

	return call

def get_prompt_header(mask):
	'''
	mask: [1/0 x 6], denotes whether each prompt component is used

	output: prompt
	'''
	url_1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&term=LMP10'
	call_1 = call_api(url_1)

	url_2 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&retmax=5&retmode=json&id=19171,5699,8138'
	call_2 = call_api(url_2)

	url_3 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&retmax=10&retmode=json&id=1217074595' 
	call_3 = call_api(url_3)

	url_4 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&term=Meesmann+corneal+dystrophy'
	call_4 = call_api(url_4)

	url_5 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=omim&retmax=20&retmode=json&id=618767,601687,300778,148043,122100'
	call_5 = call_api(url_5)

	url_6 = 'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE=XML&QUERY=ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT&HITLIST_SIZE=5'
	call_6 = call_api(url_6)
	rid = re.search('RID = (.*)\n', call_6.decode('utf-8')).group(1)

	url_7 = f'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID={rid}'
	time.sleep(30)
	call_7 = call_api(url_7)

	prompt = ''
	prompt += 'Hello. Your task is to use NCBI Web APIs to answer genomic questions.\n'
	#prompt += 'There are two types of Web APIs you can use: Eutils and BLAST.\n\n'

	if mask[0]:
		# Doc 0 is about Eutils
		prompt += 'You can call Eutils by: "[https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{esearch|efetch|esummary}.fcgi?db={gene|snp|omim}&retmax={}&{term|id}={term|id}]".\n'
		prompt += 'esearch: input is a search term and output is database id(s).\n'
		prompt += 'efectch/esummary: input is database id(s) and output is full records or summaries that contain name, chromosome location, and other information.\n'
		prompt += 'Normally, you need to first call esearch to get the database id(s) of the search term, and then call efectch/esummary to get the information with the database id(s).\n'
		prompt += 'Database: gene is for genes, snp is for SNPs, and omim is for genetic diseases.\n\n'

	if mask[1]:
		# Doc 1 is about BLAST
		prompt += 'For DNA sequences, you can use BLAST by: "[https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD={Put|Get}&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE={XML|Text}&QUERY={sequence}&HITLIST_SIZE={max_hit_size}]".\n'
		prompt += 'BLAST maps a specific DNA {sequence} to its chromosome location among different specices.\n'
		prompt += 'You need to first PUT the BLAST request and then GET the results using the RID returned by PUT.\n\n'

	if any(mask[2:]):
		prompt += 'Here are some examples:\n\n'

	if mask[2]:
		# Example 1 is from gene alias task 
		prompt += f'Question: What is the official gene symbol of LMP10?\n'
		prompt += f'[{url_1}]->[{call_1}]\n' 
		prompt += f'[{url_2}]->[{call_2}]\n'
		prompt += f'Answer: PSMB10\n\n'

	if mask[3]:
		# Example 2 is from SNP gene task
		prompt += f'Question: Which gene is SNP rs1217074595 associated with?\n'
		prompt += f'[{url_3}]->[{call_3}]\n'
		prompt += f'Answer: LINC01270\n\n'

	if mask[4]:
		# Example 3 is from gene disease association
		prompt += f'Question: What are genes related to Meesmann corneal dystrophy?\n'
		prompt += f'[{url_4}]->[{call_4}]\n'
		prompt += f'[{url_5}]->[{call_5}]\n'
		prompt += f'Answer: KRT12, KRT3\n\n'

	if mask[5]:
		# Example 4 is for BLAST
		prompt += f'Question: Align the DNA sequence to the human genome:ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT\n'
		prompt += f'[{url_6}]->[{rid}]\n'
		prompt += f'[{url_7}]->[{call_7}]\n'
		prompt += f'Answer: chr15:91950805-91950932\n\n'

	return prompt


if __name__ == '__main__':
	invalid_tasks = set(['Gene ontology', 'Gene name extraction', 'TF regulation'])
	cut_length = 18000

	str_mask = sys.argv[1]
	mask = [bool(int(x)) for x in str_mask]
	prompt = get_prompt_header(mask)

	if not os.path.isdir(str_mask):
		os.mkdir(str_mask)

	# initialize 
	prev_call = time.time()	
	#qas = json.load(open('data/newbing_qa.json'))	
	#qas = json.load(open('data/multihop_qa_into.json'))	
	qas = json.load(open('data/blast_qa.json'))	
	
	for task, info in qas.items():
		if os.path.exists(os.path.join(str_mask, f'{task}.json')):
			# continue if task is done
			preds = json.load(open(os.path.join(str_mask, f'{task}.json')))
			if len(preds) == 50: continue
		
		if task in invalid_tasks:
			continue

		output = []
		print(f'Doing task {task}')
		for question, answer in info.items():
			print('---New Instance---')
			print(question)
			q_prompt = prompt + f'Question: {question}\n'

			# save the prompting logs
			prompts = []

			# record API call times
			num_calls = 0

			while True:
				if len(q_prompt) > cut_length:
					# truncate from the start
					q_prompt = q_prompt[len(q_prompt) - cut_length:]
				
				body = {
				  "model": "code-davinci-002",
				  "prompt": q_prompt,
				  "max_tokens": 512,
				  "temperature": 0,
				  "stop": ['->', '\n\nQuestion'],
				  "n": 1
				}
				
				delta = time.time() - prev_call
				if delta < 3.1:
					time.sleep(3.1 - delta)

				try:
					prev_call = time.time()
					response = openai.Completion.create(**body)
				except openai.error.InvalidRequestError:
					output.append([question, answer, 'lengthError', prompts])
					break

				text = response['choices'][0]['text']
				print(text)
				num_calls += 1

				prompts.append([q_prompt, text])

				#url_regex = r'\[(https?*)\]'
				url_regex = r'\[(https?://[^\[\]]+)\]'
				matches = re.findall(url_regex, text)
				if matches:
				#if text[-1:] == ']' and '[' in text and 'http' in text:
					#left = text.rindex('[')
					#url = text[left + 1: -1]
					url = matches[0]
					
					# wait till the BLAST is done on NCBI server
					if 'blast' in url and 'Get' in url: time.sleep(30)
					
					call = call_api(url)

					if 'blast' in url and 'Put' in url:
						rid = re.search('RID = (.*)\n', call.decode('utf-8')).group(1)
						call = rid
					
					if len(call) > 10000:
						call = call[:10000]

					q_prompt = f'{q_prompt}{text}->[{call}]\n'

				else:
					output.append([question, answer, text, prompts])
					break

				# prevent too many calls
				if num_calls >= 10:
					output.append([question, answer, 'numError', prompts])
					break

		with open(os.path.join(str_mask, f'{task}.json'), 'w') as f:
			json.dump(output, f, indent=4)

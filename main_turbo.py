__author__ = 'qiao'

'''
GeneGPT: teach LLMs to use NCBI API
'''

import json
import config
import openai
openai.api_key = config.API_KEY

import os
import re
import sys
import time
import urllib.request

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
	# rough number of chars for truncating 
	# 16k tokens ~ 36k chars 
	cut_length = 36000

	# str_mask is a string of six 0/1 marking whether a in-context learning component is used 
	# six digits correspond to Dc. 1-2, Dm. 1-4
	str_mask = sys.argv[1]
	mask = [bool(int(x)) for x in str_mask]
	prompt = get_prompt_header(mask)

	# results are saved in the dir of six digits
	if not os.path.isdir(str_mask):
		os.mkdir(str_mask)

	# initialize 
	prev_call = time.time()	
	qas = json.load(open('data/geneturing.json'))
	
	for task, info in qas.items():
		if os.path.exists(os.path.join(str_mask, f'{task}.json')):
			# continue if task is done
			preds = json.load(open(os.path.join(str_mask, f'{task}.json')))
			if len(preds) == 50: continue
			output = preds

		else:
			output = []

		done_questions = set([entry[0] for entry in output])

		print(f'Doing task {task}')
		for question, answer in info.items():

			if question in done_questions:
				continue

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
				
				try:
					time.sleep(10)
					completion = openai.ChatCompletion.create(
							model="gpt-3.5-turbo-16k",
							messages=[
								{"role": "user", "content": q_prompt},
							],
							temperature=0.0,
							stop=["->", "\n\nQuestion"],
					)
				except openai.error.InvalidRequestError:
					output.append([question, answer, 'lengthError', prompts])
					break

				text = completion.choices[0].message["content"]

				num_calls += 1

				prompts.append([q_prompt, text])

				url_regex = r'\[(https?://[^\[\]]+)\]'
				matches = re.findall(url_regex, text)
				if matches:
					url = matches[0]
					
					# wait till the BLAST is done on NCBI server
					if 'blast' in url and 'Get' in url: time.sleep(30)
					
					call = call_api(url)

					if 'blast' in url and 'Put' in url:
						rid = re.search('RID = (.*)\n', call.decode('utf-8')).group(1)
						call = rid
					
					if len(call) > 20000:
						call = call[:20000]

					q_prompt = f'{q_prompt}{text}->[{call}]\n'

				else:
					output.append([question, answer, text, prompts])
					break

				# prevent dead loops 
				if num_calls >= 10:
					output.append([question, answer, 'numError', prompts])
					break

			with open(os.path.join(str_mask, f'{task}.json'), 'w') as f:
				json.dump(output, f, indent=4)

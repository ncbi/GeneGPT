__author__ = 'qiao'

'''
evaluate GeneGPT on all GeneTuring tasks and one GeneHop task (Disease gene location)
'''

import glob
import json
import os
import sys

def get_answer(answer, task):

	mapper = {'Caenorhabditis elegans': 'worm',
			  'Homo sapiens': 'human',
			  'Danio rerio': 'zebrafish',
			  'Mus musculus': 'mouse',
			  'Saccharomyces cerevisiae': 'yeast',
			  'Rattus norvegicus': 'rat',
			  'Gallus gallus': 'chicken'}

	if task == 'SNP location':
		answer = answer.strip().split()[-1]
		if 'chr' not in answer:
			answer = 'chr' + answer

	elif task == 'Gene location':
		answer = answer.strip().split()[-1]
		if 'chr' not in answer:
			answer = 'chr' + answer

	elif task == 'Gene disease association':
		answer = answer.strip().replace('Answer: ', '')
		answer = answer.split(', ')

	elif task == 'Disease gene location':
		answer = answer.strip().replace('Answer: ', '')
		answer = answer.split(', ')

	elif task == 'Protein-coding genes':
		answer = answer.strip().replace('Answer: ', '')
		if answer == 'Yes':
			answer = 'TRUE'
		elif answer == 'No':
			answer = 'NA'

	elif task == 'Multi-species DNA aligment':
		answer = answer.strip().replace('Answer: ', '')
		answer = mapper.get(answer, answer)

	else:
		answer = answer.strip().replace('Answer: ', '')
	
	return answer


if __name__ == '__main__':
	qas = json.load(open('data/geneturing.json'))	
	qas['Disease gene location'] = json.load(open('data/genehop.json'))['Disease gene location']

	folder = sys.argv[1]

	for task in glob.glob(os.path.join(folder, '*')):
		print(f'\nEvaluating {task}')
		preds = json.load(open(task))
		task = os.path.basename(task).replace('.json', '')

		if task not in qas:
			print(f'{task} is not automatically evaluated.')
			continue

		info = qas[task]
		pred_q2a = {}

		for entry in preds:
			pred_q2a[entry[0]] = get_answer(entry[2], task)
		
		correct = []

		for question, answer in info.items():
			if task == 'Gene disease association':
				answer = answer.split(', ')
				answer_in = [ans in pred_q2a[question] for ans in answer]
				correct.append(sum(answer_in) / len(answer_in))

			elif task == 'Disease gene location':
				answer_in = [ans in pred_q2a[question] for ans in answer]
				correct.append(sum(answer_in) / len(answer_in))

			elif task == 'Human genome DNA aligment':
				pred = pred_q2a[question]
				pred_chr = pred.split(':')[0]
				answer_chr = answer.split(':')[0]

				if pred == answer:
					correct.append(1)
				elif pred_chr == answer_chr:
					correct.append(0.5)
				else:
					correct.append(0)

			else:
				if pred_q2a[question] == answer:
					correct.append(1)
				else:
					correct.append(0)

		print(sum(correct) / len(correct))

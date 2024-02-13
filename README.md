# GeneGPT

This directory contains code and data for GeneGPT, a tool-augmented LLM for improved access to biomedical information. 
![image](https://github.com/ncbi/GeneGPT/assets/32558774/a18e142f-0742-4c14-a45f-386e9811c85d)

# Introduction

While large language models (LLMs) have been successfully applied to various tasks, they still face challenges with hallucinations, especially for specialized knowledge. We propose GeneGPT, a novel approach to address this challenge by teaching LLMs to exploit biomedical tools, specifically NCBI Web APIs, for answering information-seeking questions. Our approach utilizes in-context learning, coupled with a novel decoding algorithm that can identify and execute API calls. Empirical results show that GeneGPT achieves state-of-the-art (SOTA) performance on eight GeneTuring tasks with an average score of 0.83, largely surpassing previous SOTA (0.44 by New Bing), biomedical LLMs such as BioGPT (0.04), and ChatGPT (0.12). Further analyses suggest that: Firstly, API demonstrations are more effective than documentations for in-context tool learning; Secondly, GeneGPT can generalize to longer chains of API calls and answer multi-hop questions; Lastly, the unique and task-specific errors made by GeneGPT provide valuable insights for future improvements. Our results underline the potential of integrating domain-specific tools with LLMs for improved access and accuracy in specialized knowledge areas.

## Requirements

The code has been tested with Python 3.9.13. Please first install the required packages by:
```bash
pip install -r requirements.txt
```

You also need an OpenAI API key to run GeneGPT with Codex. Replace the placeholder with your key in `config.py`:
```bash
$ cat config.py 
API_KEY = 'YOUR_OPENAI_API_KEY'
```

## Using GeneGPT

After setting up the environment, one can run GeneGPT on GeneTuring by:
```bash
python main.py 111111
```
where `111111` denotes that all Documentations (Dc.1-2) and Demonstractions (Dm.1-4) are used.

To run GeneGPT-slim, simply use:
```bash
python main.py 001001
```
which will only use the Dm.1 and Dm.4 for in-context learning.

## Evaluating GeneGPT

One can evaluate the results by running:
```bash
python evaluate.py ${RESULT_DIRECTORY}
```

For example, we also put our experimental results in `geneturing_results` and `geneturing_results`. By running:
```bash
python evaluate.py geneturing_results/001001/
```
The user can get the evaluation results of GeneGPT-slim:
```bash
Evaluating geneturing_results/001001/Gene alias.json
0.84

Evaluating geneturing_results/001001/Gene disease association.json
0.6613333333333332

Evaluating geneturing_results/001001/Gene location.json
0.66

Evaluating geneturing_results/001001/Human genome DNA aligment.json
0.44

Evaluating geneturing_results/001001/Multi-species DNA aligment.json
0.88

Evaluating geneturing_results/001001/Gene name conversion.json
1.0

Evaluating geneturing_results/001001/Protein-coding genes.json
1.0

Evaluating geneturing_results/001001/Gene SNP association.json
1.0

Evaluating geneturing_results/001001/SNP location.json
0.98
```

## Acknowledgments

This work was supported by the Intramural Research Programs of the National Institutes of Health, National Library of Medicine.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

## Citation

If you find this repo helpful, please cite GeneGPT by:
```bibtex
@misc{jin2023genegpt,
      title={GeneGPT: Augmenting Large Language Models with Domain Tools for Improved Access to Biomedical Information}, 
      author={Qiao Jin and Yifan Yang and Qingyu Chen and Zhiyong Lu},
      year={2023},
      eprint={2304.09667},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

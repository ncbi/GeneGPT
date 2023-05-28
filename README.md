# GeneGPT

This directory contains code and data for GeneGPT, a tool-augmented LLM for improved access to biomedical information. 
![image](https://github.com/ncbi/GeneGPT/assets/32558774/c7b894eb-5ce3-4aa3-adee-01f6c2801c46)

# Introduction

While large language models (LLMs) have been successfully applied to various tasks, they still face challenges with hallucinations, especially for specialized knowledge. We propose GeneGPT, a novel approach to address this challenge by teaching LLMs to exploit biomedical tools, specifically NCBI Web APIs, for answering information-seeking questions. Our approach utilizes in-context learning, coupled with a novel decoding algorithm that can identify and execute API calls. Empirical results show that GeneGPT achieves state-of-the-art (SOTA) performance on eight GeneTuring tasks with an average score of 0.83, largely surpassing previous SOTA (0.44 by New Bing), biomedical LLMs such as BioGPT (0.04), and ChatGPT (0.12). Further analyses suggest that: Firstly, API demonstrations are more effective than documentations for in-context tool learning; Secondly, GeneGPT can generalize to longer chains of API calls and answer multi-hop questions; Lastly, the unique and task-specific errors made by GeneGPT provide valuable insights for future improvements. Our results underline the potential of integrating domain-specific tools with LLMs for improved access and accuracy in specialized knowledge areas.

## Requirements



## Using GeneGPT



## Evaluating GeneGPT



## Acknowledgments

This work was supported by the Intramural Research Programs of the National Institutes of Health, National Library of Medicine.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.

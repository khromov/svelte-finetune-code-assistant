# Fine-tuning your own code completion model

Blog post: [Build Your Own GitHub Copilot](https://prvn.sh/build-your-own-github-copilot/)

This repo contains:
  1. Scripts for generating a fill-in-the-middle (FIM) dataset from a codebase (only works for Svelte projects at the moment)
  2. A Jupyter notebook for running SFT on the generated FIM dataset 

# Generating the dataset

```
cd src/dataset_gen && npm install
node gen.js <path to svelte repo>
```

Then follow the notebook for running SFT on the training data. 

# Computing metrics
If you follow the notebook, you should have a `generated.test.jsonl` (or `generated-post-finetune.test.jsonl`) file containing the prefix, suffix, expected completion and actual completion.

You can then run `python src/metrics.py <path to generated jsonl file>` to get some basic accuracy and BLEU metrics.

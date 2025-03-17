import sys
import json
from nltk.tokenize import TreebankWordTokenizer
from nltk.translate.bleu_score import corpus_bleu

tokenizer = TreebankWordTokenizer()

def compute_eval_metrics(generated_file):
    total = 0
    correct = 0
    bleu_generated_tokens = []
    bleu_expected_tokens = []
    with open(generated_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            generated = data["generated"]
            generated = generated.replace("<|file_sep|>", "").replace("<|fim_pad|>", "")
            expected = data["expected"]

            if generated == expected:
                correct += 1
            total += 1

            # BLEU score
            bleu_generated_tokens.append(tokenizer.tokenize(generated))
            bleu_expected_tokens.append([tokenizer.tokenize(expected)])

    print(f'Total: {total}')
    print(f'[Exact Match] Correct: {correct}')
    print(f'[Exact Match] Accuracy: {correct/total:.2f}')
    print(f'BLEU Score: {corpus_bleu(bleu_expected_tokens, bleu_generated_tokens):.4f}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python metrics.py <generated_file>")
        sys.exit(1)
    
    compute_eval_metrics(sys.argv[1])
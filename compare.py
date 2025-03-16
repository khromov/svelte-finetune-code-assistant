import sys
import json
import random
import hashlib

def hash(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def get_line_from_file(file_path, line_idx):
    with open(file_path) as f:
        for i, line in enumerate(f):
            if i == line_idx:
                return line.strip()

def compare(baseline, post_finetune, idx=None):
    with open(baseline) as f:
        baseline_lines = f.readlines()
        baseline_keys = [hash(json.loads(line)['prefix']) for line in baseline_lines]
    
    with open(post_finetune) as f:
        pf_lines = f.readlines()
        pf_keys = [hash(json.loads(line)['prefix']) for line in pf_lines]
    
    num_lines = len(baseline_lines)
    baseline_idx = idx if idx is not None else random.randint(0, num_lines - 1)

    chosen_key = baseline_keys[baseline_idx]
    pf_idx = pf_keys.index(chosen_key)

    baseline_data = json.loads(baseline_lines[baseline_idx])
    post_finetune_data = json.loads(pf_lines[pf_idx])

    prefix = baseline_data['prefix']
    suffix = baseline_data['suffix']
    expected = baseline_data['expected']

    baseline_gen = baseline_data['generated'].replace('<|file_sep|>', '').replace('<|fim_pad|>', '')
    post_finetune_gen = post_finetune_data['generated'].replace('<|file_sep|>', '').replace('<|fim_pad|>', '')

    print(f'Example #{baseline_idx}')
    print(f'{prefix}<expected>{expected}</expected><baseline>{baseline_gen}</baseline><post_finetune>{post_finetune_gen}</post_finetune>{suffix}')

if __name__ == '__main__':
    baseline = sys.argv[1]
    post_finetune = sys.argv[2]
    idx = None
    if len(sys.argv) == 4:
        idx = int(sys.argv[3])
    compare(baseline, post_finetune, idx)
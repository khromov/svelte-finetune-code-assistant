import argparse
import html

def generate_diff_html(prefix, suffix, expected, baseline, post_finetune):
    """
    Generate GitHub-style diff HTML for comparing model outputs.
    
    Args:
        prefix (str): The code prefix before the completion
        suffix (str): The code suffix after the completion
        expected (str): The expected completion
        baseline (str): The baseline model completion
        post_finetune (str): The post-finetuning model completion
    
    Returns:
        str: The generated HTML content
    """
    # Escape HTML in all inputs
    prefix = html.escape(prefix)
    suffix = html.escape(suffix)
    expected = html.escape(expected)
    baseline = html.escape(baseline)
    post_finetune = html.escape(post_finetune)
    
    # Split the code into lines
    expected_lines = expected.strip().split('\n')
    baseline_lines = baseline.strip().split('\n')
    post_finetune_lines = post_finetune.strip().split('\n')
    
    # Generate the HTML content
    html_content = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #24292e; background-color: #f6f8fa; margin: 0; margin-top: 20px">
  <div style="margin: 0 auto; background-color: #fff; border: 1px solid #e1e4e8; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <div style="padding: 8px 16px; background-color: #f6f8fa; border-bottom: 1px solid #e1e4e8; font-weight: 600; font-size: 14px; display: flex; justify-content: space-between; align-items: center;">
      <span style="color: #24292e;">Code Comparison</span>
      <span style="color: #6a737d; font-size: 12px;">Fill-in-middle comparison</span>
    </div>
    
    <div style="background-color: #f6f8fa; padding: 8px 16px; color: #24292e; font-size: 12px; border-bottom: 1px solid #e1e4e8;">
      <div style="font-weight: 600; margin-bottom: 5px;">Function Implementation Comparison</div>
      <div style="color: #6a737d;">3 versions: expected, baseline, post-finetune</div>
    </div>
    
    <div style="font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace; font-size: 12px; line-height: 1.5; tab-size: 2; overflow-x: auto;">
      <table style="width: 100%; border-spacing: 0;">
        <tbody>
"""

    # Add prefix
    line_number = 1
    for line in prefix.split('\n'):
        html_content += f"""          <tr style="height: 1.5em;">
            <td style="text-align: right; padding: 0 8px; width: 1%; min-width: 50px; color: #6a737d; background-color: #f6f8fa; border-right: 1px solid #e1e4e8; user-select: none;">{line_number}</td>
            <td style="padding: 0 10px; white-space: pre; background-color: #f6f8fa;"><span style="color: #24292e;">{line}</span></td>
          </tr>
"""
        line_number += 1

    # Add expected implementation
    for i, line in enumerate(expected_lines):
        html_content += f"""          <tr style="height: 1.5em;" onmouseover="this.style.backgroundColor='#fffbdd'; this.children[0].style.backgroundColor='#fffbdd';" onmouseout="this.style.backgroundColor='#e6ffec'; this.children[0].style.backgroundColor='#e6ffec';">
            <td style="text-align: right; padding: 0 8px; width: 1%; min-width: 50px; color: #6a737d; background-color: #e6ffec; border-right: 1px solid #e1e4e8; user-select: none;">{line_number}</td>
            <td style="padding: 0 10px; white-space: pre; background-color: #e6ffec;">{line}</td>
          </tr>
"""
        line_number += 1

    # Add baseline implementation
    line_number = len(prefix.split('\n')) + 1  # Reset line number for baseline
    for i, line in enumerate(baseline_lines):
        html_content += f"""          <tr style="height: 1.5em;" onmouseover="this.style.backgroundColor='#fffbdd'; this.children[0].style.backgroundColor='#fffbdd';" onmouseout="this.style.backgroundColor='#ffebe9'; this.children[0].style.backgroundColor='#ffebe9';">
            <td style="text-align: right; padding: 0 8px; width: 1%; min-width: 50px; color: #6a737d; background-color: #ffebe9; border-right: 1px solid #e1e4e8; user-select: none;">{line_number + i}</td>
            <td style="padding: 0 10px; white-space: pre; background-color: #ffebe9;">{line}</td>
          </tr>
"""

    # Add post-finetune implementation
    line_number = len(prefix.split('\n')) + 1  # Reset line number for post-finetune
    for i, line in enumerate(post_finetune_lines):
        html_content += f"""          <tr style="height: 1.5em;" onmouseover="this.style.backgroundColor='#fffbdd'; this.children[0].style.backgroundColor='#fffbdd';" onmouseout="this.style.backgroundColor='#ddf4ff'; this.children[0].style.backgroundColor='#ddf4ff';">
            <td style="text-align: right; padding: 0 8px; width: 1%; min-width: 50px; color: #6a737d; background-color: #ddf4ff; border-right: 1px solid #e1e4e8; user-select: none;">{line_number + i}</td>
            <td style="padding: 0 10px; white-space: pre; background-color: #ddf4ff;">{line}</td>
          </tr>
"""

    # Add suffix
    line_number = len(prefix.split('\n')) + max(len(expected_lines), len(baseline_lines), len(post_finetune_lines))
    for line in suffix.split('\n'):
        html_content += f"""          <tr style="height: 1.5em;">
            <td style="text-align: right; padding: 0 8px; width: 1%; min-width: 50px; color: #6a737d; background-color: #f6f8fa; border-right: 1px solid #e1e4e8; user-select: none;">{line_number + 1}</td>
            <td style="padding: 0 10px; white-space: pre; background-color: #f6f8fa;">{line}</td>
          </tr>
"""
        line_number += 1

    # Add footer
    html_content += """        </tbody>
      </table>
    </div>
    
    <div style="border-top: 1px solid #e1e4e8; padding: 10px 16px; display: flex; gap: 10px;">
      <span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 500; color: white; background-color: #2da44e;">Expected</span>
      <span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 500; color: white; background-color: #cf222e;">Baseline</span>
      <span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 500; color: white; background-color: #0969da;">Post-Finetune</span>
    </div>
  </div>
</div>"""

    return html_content

def main():
    parser = argparse.ArgumentParser(description='Generate GitHub-style diff HTML for comparing model outputs.')
    parser.add_argument('--prefix', required=True, help='Code prefix before the completion')
    parser.add_argument('--suffix', required=True, help='Code suffix after the completion')
    parser.add_argument('--expected', required=True, help='Expected completion')
    parser.add_argument('--baseline', required=True, help='Baseline model completion')
    parser.add_argument('--post-finetune', required=True, help='Post-finetuning model completion')
    parser.add_argument('--output', required=True, help='Output HTML file')
    
    args = parser.parse_args()
    
    html_content = generate_diff_html(
        args.prefix, 
        args.suffix, 
        args.expected, 
        args.baseline, 
        args.post_finetune
    )
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML file generated: {args.output}")

if __name__ == "__main__":
    main()

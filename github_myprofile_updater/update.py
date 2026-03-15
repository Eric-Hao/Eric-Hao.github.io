import os

if __name__ == '__main__':
    _header = '## Hi there 👋'
    # Use absolute paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '../_pages/includes/')
    
    with open(os.path.join(base_dir, 'intro_short.md'), 'r') as f:
        _intro_short = f.read().strip().replace("2.8em", "3em")
        
    with open(os.path.join(base_dir, 'news.md'), 'r') as f:
        _news = f.read().strip()
    _news = _news.split("# News")[-1]
    
    readme_path = os.path.join(script_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(_header)
        f.write('\n\n')
        f.write(_intro_short)
        f.write('\n\n## News\n\n')
        f.write(_news)
        f.write('\n')


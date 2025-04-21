if __name__ == '__main__':
    _header = '## Hi there 👋'
    base_dir = '../_pages/includes/'
    _intro_short = open(f'{base_dir}/intro_short.md').read().strip().replace("2.8em", "3em")
    _news = open(f'{base_dir}/news.md').read().strip()
    with open('README.md', 'w') as f:
        f.write(_header)
        f.write('\n\n')
        f.write(_intro_short)
        f.write('\n\n##')
        f.write(_news)

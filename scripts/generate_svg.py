import os
import requests
import sys
from datetime import datetime


GITHUB_API = 'https://api.github.com'
USERNAME = os.environ.get('USERNAME') or 'rafael-serafin1'
TOKEN = os.environ.get('GITHUB_TOKEN')


HEADERS = {'Accept': 'application/vnd.github+json'}
if TOKEN:
    HEADERS['Authorization'] = f'token {TOKEN}'




def fetch_user(username):
    r = requests.get(f'{GITHUB_API}/users/{username}', headers=HEADERS)
    r.raise_for_status()
    return r.json()




def fetch_repos(username):
    repos = []
    page = 1
    while True:
        r = requests.get(f'{GITHUB_API}/users/{username}/repos', headers=HEADERS, params={'per_page': 100, 'page': page, 'type': 'owner', 'sort': 'updated'})
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos




def summarize(repos):
    total_stars = sum(r.get('stargazers_count', 0) for r in repos)
    total_forks = sum(r.get('forks_count', 0) for r in repos)
    total_repos = len(repos)
    langs = {}
    for r in repos:
        lang = r.get('language') or 'Unknown'
        langs[lang] = langs.get(lang, 0) + 1
    top_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        'stars': total_stars,
        'forks': total_forks,
        'repos': total_repos,
        'top_langs': top_langs,
    }




def render_svg(username, user, summary):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    top_langs_str = ', '.join(f'{l} ({c})' for l, c in summary['top_langs'])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="540" height="160" viewBox="0 0 540 160">
        <rect width="100%" height="100%" rx="4" fill="#0f172a" />

        <g transform="translate(35,35)">
            <text x="0" y="0" fill="#7dd3fc" font-weight="600">{username}</text>
            <text x="0" y="22" fill="#94a3b8">{user.get('name','') or ''} &#8226; {user.get('bio','') or ''}</text>

            <g transform="translate(0,50)">
                <text x="0" y="0" fill="#facc15">Stars: {summary['stars']}</text>
                <text x="160" y="0" fill="#facc15">Repos: {summary['repos']}</text>
                <text x="320" y="0" fill="#facc15">Forks: {summary['forks']}</text>

                <text x="0" y="28" fill="#a5f3fc">Top languages: {top_langs_str}</text>
                <text x="0" y="46" fill="#e2e8f0">Followers: {user.get('followers', 0)} &#8226; Updated: {now}</text>
            </g>
        </g>
    </svg>'''
    return svg

def main():
    try:
        user = fetch_user(USERNAME)
        repos = fetch_repos(USERNAME)
        summary = summarize(repos)
        svg = render_svg(USERNAME, user, summary)
        svg = svg.lstrip().replace('\ufeff', '')

        with open('stats.svg', 'w', encoding='utf-8') as f:
            f.write(svg)

        print('stats.svg generated')
    except Exception as e:
        print('Error:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
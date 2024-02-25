from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

conn = sqlite3.connect('search_results.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS search_results
             (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, keyword TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    urls = get_search_results(keyword)
    save_to_database(urls, keyword)
    return redirect(url_for('show_results', keyword=keyword))

def get_search_results(keyword):
    url = f'https://www.google.com/search?q={keyword}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
    return urls

def save_to_database(urls, keyword):
    conn = sqlite3.connect('search_results.db')
    c = conn.cursor()
    for url in urls:
        c.execute("INSERT INTO search_results (url, keyword) VALUES (?, ?)", (url, keyword))
    conn.commit()
    conn.close()

@app.route('/results/<keyword>')
def show_results(keyword):
    conn = sqlite3.connect('search_results.db')
    c = conn.cursor()
    c.execute("SELECT url FROM search_results WHERE keyword=? ORDER BY id DESC", (keyword,))
    results = c.fetchall()
    conn.close()
    return render_template('results.html', keyword=keyword, results=results)

if __name__ == '__main__':
    app.run(debug=True)

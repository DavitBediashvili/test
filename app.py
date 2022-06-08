from flask import Flask, redirect, url_for, render_template
import json
import requests
h = {"Accept-Language": "en-US"}
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

url1 = "https://www.rottentomatoes.com/browse/movies_at_home/critics:certified_fresh~sort:popular?page=1"

popular_dict = dict()
rating_dict = dict()

req = requests.get(url1, headers=h)
html = req.text
soup = BeautifulSoup(html, 'html.parser')
sub_soup = soup.find('div', {'class': 'discovery-grids-container'})
sub_soup1 = sub_soup.find('div', {'class': 'discovery-tiles__wrap'})
sub_soup2 = sub_soup1.find_all('a')
for each in sub_soup2:
    photo = each.find('img')
    title = each.find('span')
    popular_dict[title.text] = photo["data-src"]

for each in sub_soup2:
    sub_soup4 = each.find('div', slot="caption")
    ratings = sub_soup4.find('score-pairs')
    user = ratings["audiencescore"]
    critic = ratings["criticsscore"]
    title = sub_soup4.find("span").text
    rating_dict[title] = f"User Rating: {user} and Critics Rating: {critic}"



url = 'https://www.swoop.ge/events'
movies_dict = dict()
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
soup_sub = soup.find_all('div', {'class': 'movies-deal'})

names_list = list()
for each in soup_sub:

    soup_sub1 = each.find('div', {'class': 'movie-name'})
    title = soup_sub1.find('p')
    if title.text == 'კინოთეატრი ამირანი':
        break
    else:
        names_list.append(title.text)


img_list = list()
for each in soup_sub:
    soup_sub_img = each.find('div', {'class': 'movie-main-img'})
    soup_sub_img_link = soup_sub_img.find('img')
    if "/Images/NewDesigneImg/" in soup_sub_img_link["src"]:
        break
    else:
        img_list.append(soup_sub_img_link["src"])


swoop_dict = dict()
for i in range(len(names_list)):
    swoop_dict[names_list[i]] = img_list[i]










@app.route('/')
def home(popular_dict=popular_dict, rating_dict=rating_dict):
    return render_template('home.html', popular_dict=popular_dict, rating_dict=rating_dict)


@app.route('/now_showing')
def now_showing():
    return render_template('now_showing.html')


@app.route('/sales')
def sales(swoop_dict=swoop_dict):
    return render_template('sales.html', swoop_dict=swoop_dict)


@app.route('/search_actor')
def search_actor():
    return render_template('search_actor.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


app.run(debug=True)
from flask import Flask, redirect, url_for, render_template, flash, request, session, abort
import json
import os
from werkzeug.utils import secure_filename
import requests
h = {"Accept-Language": "en-US"}
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'zdarova'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Umagresi_Reviewebi.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    film = db.Column(db.String(20), nullable=False)
    comments = db.Column(db.String(30), nullable=False)

    def str(self):
        return f'Film: {self.film} | comment: {self.comments}'


db.create_all()

m1 = dict()
all_comments = Review.query.all()
for each in all_comments:
    m1[each.film] = each.comments





class Galler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def str(self):
        return f'{self.film}, {self.comments}'


db.create_all()

#Home
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
    rating_dict[title] = f"Audience Rating: {user} and Critics Rating: {critic}"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/home')
def home():
    return render_template('home.html', popular_dict=popular_dict, rating_dict=rating_dict)


m1 = dict()
@app.route('/Review', methods=['POST', 'GET'])
def review():
    db.create_all()
    all_comments = Review.query.all()

    for each in all_comments:
        m1[each.film] = each.comments
    if request.method == "POST":
        comments = request.form['comments']
        film = request.form['film']
        f1 = Review(film=film, comments=comments)
        if comments == '' or film == '':
            flash("ჯერ დაწერე")
        else:
            db.session.add(f1)
            db.session.commit()
            flash("It is what it is")

    return render_template('now_showing.html', m1 = m1)

info = ''
gallery_dict = dict()

@app.route('/Gallery', methods=['GET', 'POST'])
def Gallery():
    if request.method=='POST':
        info = request.form['info']
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            G1 = Galler(text=info, name=filename)
            db.session.add(G1)
            db.session.commit()

    all_gal = Galler.query.all()
    for each1 in all_gal:
        gallery_dict[each1.name] = each1.text
    return render_template('sales.html', gallery_dict=gallery_dict)



@app.route('/search_actor', methods=['GET', 'POST'])
def search_actor():
    img_dict = dict()
    rate_dict = dict()
    bio_dict = dict()
    actor_name = ""
    img_link = ""
    best_movie = ""
    birth_day = ""
    bio = ""
    name = None
    if request.method=='POST':
        name = request.form['name']
    # actor search

    if name != None:
        name_changed = name.replace(" ", "_").lower()
        url_tomato = f'https://www.rottentomatoes.com/celebrity/{name_changed}'
        req = requests.get(url_tomato, headers=h)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        sub_soup = soup.find('div', id="main-page-content")
        sub_soup2 = sub_soup.find('div', {'class': 'layout celebrity'})
        if sub_soup2 == None:
            return abort(404, "we could not find actor")
        else:
            sub_soup3 = sub_soup2.find('a')
            sub_soup4 = sub_soup3.find('img')

            sub_soup_name = sub_soup2.find('div', {'class': 'celebrity-bio__content'})
            sub_soup_name1 = sub_soup_name.find('h1')

            sub_soup_movie = sub_soup_name.find('div', {'class': 'celebrity-bio__info'})
            sub_soup_movie1 = sub_soup_movie.find('p', {'data-qa': 'celebrity-bio-highest-rated'})
            sub_soup_movie2 = sub_soup_movie1.find('span')
            sub_soup_movie3 = sub_soup_movie2.find('a')

            sub_soup_birth = sub_soup_movie.find('p', {'data-qa': 'celebrity-bio-bday'})

            sub_soup_bio = sub_soup_movie.find('p', {'data-qa': 'celebrity-bio-summary'})

            actor_name = sub_soup_name1.text
            img_link = sub_soup4['data-src']
            best_movie = sub_soup_movie3.text
            if best_movie == None:
                pass
            else:
                birth_day = sub_soup_birth.text
                bio_unedited = sub_soup_bio.text.split(".", 1)
                bio = bio_unedited[0]

                movies_soup = sub_soup.find('section', {'class': 'celebrity-filmography'})
                movies_soup1 = movies_soup.find('div', {'class': 'scroll-x'})
                movies_soup2 = movies_soup1.find('tbody', {'class': 'celebrity-filmography__tbody'})
                movies_soup3 = movies_soup2.find_all('tr')
                index = 0
                for each in movies_soup3:
                    if each["data-audiencescore"] != "0":
                        if index == 6:
                            break
                        else:
                            pass
                        title = each["data-title"].replace(" ", "_").lower()
                        url_movie_web = f'https://www.rottentomatoes.com/m/{title}'
                        req = requests.get(url_movie_web, headers=h)
                        html = req.text
                        soup = BeautifulSoup(html, 'html.parser')
                        movie_web_soup = soup.find('div',
                                                   {'class': "col mob col-center-right col-full-xs mop-main-column"})
                        if movie_web_soup == None:
                            continue
                        else:
                            pass
                        movie_web_soup1 = movie_web_soup.find('div', id="topSection")
                        movie_web_soup2 = movie_web_soup1.find('div', {'class': 'movie-thumbnail-wrap'})
                        movie_web_soup3 = movie_web_soup2.find('img')
                        string_movie = str(movie_web_soup3)[54:].split('"', 1)
                        img_link_movie = string_movie[0]

                        movie_title_soup = movie_web_soup1.find('div', {'class': "thumbnail-scoreboard-wrap"})
                        movie_title_soup1 = movie_title_soup.find('score-board')
                        movie_title_soup2 = movie_title_soup1.find('h1')
                        title_link_movie = movie_title_soup2.text
                        aud_rate = movie_title_soup1['audiencescore']

                        img_dict[title_link_movie] = img_link_movie
                        rate_dict[title_link_movie] = aud_rate

                        index += 1

                        exact_movie_bio = movie_web_soup.find('section', {'data-qa': 'movie-info-section'})
                        exact_movie_bio1 = exact_movie_bio.find('div', id="movieSynopsis").text
                        bio_dict[title_link_movie] = exact_movie_bio1
                    else:
                        pass



    else:
        actor_name = None
        img_link = None
        best_movie = None
        birth_day = None
        bio_unedited = None
        bio = None



    return render_template('search_actor.html', actor_name=actor_name, img_link=img_link, best_movie=best_movie, birth_day=birth_day, bio=bio, img_dict=img_dict, rate_dict=rate_dict, bio_dict=bio_dict)


@app.route('/')
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == "POST":

        username = request.form['username']
        session['username'] = username

        return redirect(url_for('review'))
    else:
        return render_template('profile.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    if request.method == "GET":
        return redirect(url_for('profile'))


app.run(debug=True)
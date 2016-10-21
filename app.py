from flask import Blueprint
from flask import Flask, request, render_template, url_for, redirect
main = Flask(__name__)
main.config['SECRET_KEY'] = 'DontTellAnyone'
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

import json
from engine import RecommendationEngine
 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class topForm(Form):
    user_id = StringField('User Id:', validators=[InputRequired()])
    count = StringField('Top Count:', validators=[InputRequired()])

class indvForm(Form):
    user_id = StringField('User Id:', validators=[InputRequired()])
    movie_id = StringField('Movie Id:', validators=[InputRequired()])
    

@main.route("/", methods = ["GET", "POST"])
def index():
    form = topForm()
    formIndv = indvForm()
    if form.validate_on_submit():
	#return "successful!"
	tuser_id = form.user_id.data
	tcount = form.count.data
	return redirect(url_for('top_ratings', user_id = tuser_id, count = tcount))
    if formIndv.validate_on_submit():
	indv_user = formIndv.user_id.data
        indv_mov = formIndv.movie_id.data
	return redirect(url_for('movie_ratings', user_id = indv_user, movie_id = indv_mov))
    return render_template('index.html', **locals())
 
@main.route("/<int:user_id>/ratings/top/<int:count>", methods=["GET"])
def top_ratings(user_id, count):
    logger.debug("User %s TOP ratings requested", user_id)
    top_ratings = recommendation_engine.get_top_ratings(user_id,count)
    list = json.dumps(top_ratings)
    #return json.dumps(top_ratings)
    return render_template('top_rating.html', **locals())
 
@main.route("/<int:user_id>/ratings/<int:movie_id>", methods=["GET"])
def movie_ratings(user_id, movie_id):

    #logger.debug("User %s rating requested for movie %s", user_id, movie_id)
    logger.info("User %s rating requested for movie %s", user_id, movie_id);
    ratings = recommendation_engine.get_ratings_for_movie_ids(user_id, [movie_id])
    value = json.dumps(ratings)
    return render_template('select_movie.html', value=value, user_id=user_id, movie_id=movie_id)
    #return json.dumps(ratings)
 
 
@main.route("/<int:user_id>/ratings", methods = ["POST"])
def add_ratings(user_id):
    # get the ratings from the Flask POST request object
    ratings_list = request.form.keys()[0].strip().split("\n")
    ratings_list = map(lambda x: x.split(","), ratings_list)
    # create a list with the format required by the negine (user_id, movie_id, rating)
    ratings = map(lambda x: (user_id, int(x[0]), float(x[1])), ratings_list)
    # add them to the model using then engine API
    recommendation_engine.add_ratings(ratings)
 
    return json.dumps(ratings)
 
 
def create_app(spark_context, dataset_path):
    global recommendation_engine 

    recommendation_engine = RecommendationEngine(spark_context, dataset_path)    
    
    #app = Flask(__name__)
    #app.register_blueprint(main)
    #return app
    return main 

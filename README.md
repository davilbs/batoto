heroku login
git push heroku master
heroku ps:scale bot=0
heroku ps:scale bot=1
import urllib
import webapp2
import jinja2
import os
import datetime
import pytz

from pytz import timezone
from google.appengine.api import users
from google.appengine.ext import ndb


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+ "/pages"))


class Reviews(ndb.Model):
    author = ndb.StringProperty()
    location = ndb.StringProperty()
    Review = ndb.StringProperty()
    Rating = ndb.IntegerProperty()
    review_date = ndb.DateTimeProperty(auto_now_add=True)
    

class MainPage(webapp2.RequestHandler):
    """ Handler for the front page."""

    def get(self):
        review_query = Reviews.query()
        reviews = review_query.fetch(10)

        user_tz = timezone('Asia/Singapore')
        for rev in reviews:
            rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
            
        
        user = users.get_current_user()
        if user: # signed in
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'reviews': reviews
                }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'reviews': reviews
                }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))

class LoginSucessPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
             }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
        
class PostReview(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
             }
        template = jinja_environment.get_template('post.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        review = Reviews(author=users.get_current_user().nickname(),
                         location=self.request.get('location'),
                         Review=self.request.get('review'),
                         Rating=int(self.request.get('ratings')))
        reviewID = review.put()
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
             }
        template = jinja_environment.get_template('profile.html')
        self.redirect('/reviews?reviewid=%s'%reviewID.urlsafe())
        
class ViewReviews(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        reviewID = self.request.get('reviewid')
        
        if reviewID:
            
            review = ndb.Key(urlsafe=reviewID).get()
            user_tz = timezone('Asia/Singapore')
            adjusted_date = review.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'author': review.author,
                'location': review.location,
                'review': review.Review,
                'rating': review.Rating,
                'date': adjusted_date.strftime("%H:%M %Y-%m-%d %Z"),
                }
                
            template = jinja_environment.get_template('reviewsIndividual.html')
            self.response.out.write(template.render(template_values))
        else:
            template_values= {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('profile.html')
            self.response.out.write(template.render(template_values))
    
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', LoginSucessPage),
                               ('/post', PostReview),
                               ('/reviews', ViewReviews)],
                              debug=True)

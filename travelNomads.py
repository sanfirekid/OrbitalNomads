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
    country = ndb.StringProperty()
    Country_lower = ndb.ComputedProperty(lambda self: self.country.lower())
    location = ndb.StringProperty()
    Location_lower = ndb.ComputedProperty(lambda self: self.location.lower())
    Review = ndb.StringProperty()
    Rating = ndb.IntegerProperty()
    review_date = ndb.DateTimeProperty(auto_now_add=True)

    def reserve_model_ids():
        first, last = Reviews.allocate_ids(50000)
        return first, last
    

class MainPage(webapp2.RequestHandler):
    """ Handler for the front page."""

    def get(self):
        review_query = Reviews.query().order(-Reviews.review_date)
        reviews = review_query.fetch(10)

        user_tz = timezone('Asia/Singapore')
        for rev in reviews:
            rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
            if len(rev.Review)>50:
                rev.Review = (rev.Review[:50] + "...")
            
        
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

    def post(self):
        searchQueryText = self.request.get('search')
        
        self.redirect('/search?query=%s'%searchQueryText)
        

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
                         country=self.request.get('country'),
                         location=self.request.get('location'),
                         Review=self.request.get('review'),
                         Rating=int(self.request.get('ratings')))
        reviewID = review.put()
        self.redirect('/reviews?reviewid=%s'%reviewID.urlsafe())
        
class ViewReviews(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        reviewID = self.request.get('reviewid')

        if user:
            if reviewID:
                
                review = ndb.Key(urlsafe=reviewID).get()
                user_tz = timezone('Asia/Singapore')
                adjusted_date = review.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'country': review.country,
                    'author': review.author,
                    'location': review.location,
                    'review': review.Review,
                    'rating': review.Rating,
                    'date': adjusted_date.strftime("%H:%M %d-%m-%Y %Z"),
                    }
                    
                template = jinja_environment.get_template('reviewsIndividual.html')
                self.response.out.write(template.render(template_values))
            else:
                review_query = Reviews.query().order(-Reviews.review_date)
                reviews = review_query.fetch()

                user_tz = timezone('Asia/Singapore')
                for rev in reviews:
                    rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                    if len(rev.Review)>50:
                        rev.Review = (rev.Review[:50] + "...")
                        
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'reviews': reviews
                    }
                template = jinja_environment.get_template('reviews.html')
                self.response.out.write(template.render(template_values))
        else:
            if reviewID:
                
                review = ndb.Key(urlsafe=reviewID).get()
                user_tz = timezone('Asia/Singapore')
                adjusted_date = review.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                template_values = {
                    'country': review.country,
                    'author': review.author,
                    'location': review.location,
                    'review': review.Review,
                    'rating': review.Rating,
                    'date': adjusted_date.strftime("%H:%M %d-%m-%Y %Z"),
                    }
                    
                template = jinja_environment.get_template('reviewsIndividual.html')
                self.response.out.write(template.render(template_values))
            else:
                review_query = Reviews.query().order(-Reviews.review_date)
                reviews = review_query.fetch()

                user_tz = timezone('Asia/Singapore')
                for rev in reviews:
                    rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                    if len(rev.Review)>50:
                        rev.Review = (rev.Review[:50] + "...")
                        
                template_values = {
                    'reviews': reviews
                    }
                template = jinja_environment.get_template('reviews.html')
                self.response.out.write(template.render(template_values))

                
class SearchResults(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        query = self.request.get('query')
        query_lower = query.lower()
        review_query = Reviews.query(ndb.OR(Reviews.Country_lower==query_lower,
                                            Reviews.Location_lower==query_lower)).order(
                                                -Reviews.review_date)
        search_results = review_query.fetch()

        user_tz = timezone('Asia/Singapore')
        for rev in review_query:
            rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
            if len(rev.Review)>50:
                    rev.Review = (rev.Review[:50] + "...")
        if user:
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'reviews': search_results
                }
            template = jinja_environment.get_template('reviews.html')
            self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'reviews': search_results
                }

            template = jinja.environment.get_template('reviews.html')
            self.response.out.write(template.render(template_values))

            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', LoginSucessPage),
                               ('/post', PostReview),
                               ('/reviews', ViewReviews),
                               ('/search', SearchResults)],
                              debug=True)

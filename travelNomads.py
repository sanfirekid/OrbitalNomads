import urllib
import webapp2
import jinja2
import os
import datetime
import pytz

from pytz import timezone
from google.appengine.api import users
from google.appengine.api import images
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
    author_email = ndb.StringProperty()
    tour_guide = ndb.StringProperty()
    review_date = ndb.DateTimeProperty(auto_now=True)
    
class UserProfile(ndb.Model):
    email = ndb.StringProperty()
    avatar = ndb.BlobProperty()
    
class Comments(ndb.Model):
    #reviewID = ndb.IntegerProperty()
    comments = ndb.StringProperty()
    comment_author = ndb.StringProperty()
    comment_date = ndb.DateTimeProperty(auto_now_add=True)
    
    
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
        

class LoginSucessPage(webapp2.RequestHandler):

    def get(self):
        currentUser = ndb.Key('UserProfile', users.get_current_user().nickname())
        user = currentUser.get()

        review_query = Reviews.query(Reviews.author==users.get_current_user().nickname()).order(Reviews.review_date)

        reviews = review_query.fetch()
        user_tz = timezone('Asia/Singapore')
        for rev in reviews:
            rev.review_date = rev.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
            if len(rev.Review)>50:
                rev.Review = (rev.Review[:50] + "...")

                
        if user == None:
            user = UserProfile(id=users.get_current_user().nickname())
            user.email = users.get_current_user().email()
            user.put()
                              
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'user_profile': user,
            'logout': users.create_logout_url(self.request.host_url),
            'reviews': reviews
             }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        currentUser = ndb.Key('UserProfile', users.get_current_user().nickname())
        user = currentUser.get()

        avatar = self.request.get('imgUpload')
        if avatar:
            avatar = images.resize(avatar, 32, 32)
            user.avatar = avatar
            user.put()


        template_values = {
           'user_nickname': users.get_current_user().nickname(),
           'user_profile': user,
           'logout': users.create_logout_url(self.request.host_url),
            }   
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))

class DeleteReview(webapp2.RequestHandler):

    def get(self):
        reviewID = self.request.get('reviewid')

        review = Reviews.get_by_id(int(reviewID))
        review.key.delete()
        
        self.redirect('/profile')
        

class EditReview(webapp2.RequestHandler):

    def get(self):
        reviewID = self.request.get('reviewid')

        review = Reviews.get_by_id(int(reviewID))
        
        user = users.get_current_user()
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'country': review.country,
            'location': review.location,
            'review': review.Review,
            'tour_guide': review.tour_guide,
            'rating': review.Rating,
            'logout': users.create_logout_url(self.request.host_url),
            
             }
        template = jinja_environment.get_template('post.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        reviewID = self.request.get('reviewid')

        review = Reviews.get_by_id(int(reviewID))

        review.country = self.request.get('country')
        review.location = self.request.get('location')
        review.Review = self.request.get('review')
        review.tour_guide = self.request.get('tourSelect')
        review.Rating = int(self.request.get('ratings'))

        review.put()

        self.redirect('/reviews?reviewid=%s'%reviewID)
                            
        
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
                         author_email=users.get_current_user().email(),
                         country=self.request.get('country'),
                         location=self.request.get('location'),
                         Review=self.request.get('review'),
                         tour_guide=self.request.get('tourSelect'),
                         Rating=int(self.request.get('ratings')))
        reviewID = review.put().id()
        self.redirect('/reviews?reviewid=%s'%reviewID)
        
class ViewReviews(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        reviewID = self.request.get('reviewid')

        if user:
            if reviewID:

                review = Reviews.get_by_id(int(reviewID))
                user_tz = timezone('Asia/Singapore')
                adjusted_date = review.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)

                comment_query = Comments.query(ancestor=review.key).order(Comments.comment_date)
                
                comments_all = comment_query.fetch()
                for comms in comments_all:
                    comms.comment_date = comms.comment_date.replace(tzinfo=pytz.utc).astimezone(user_tz)
                
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'country': review.country,
                    'author': review.author,
                    'location': review.location,
                    'review': review.Review,
                    'rating': review.Rating,
                    'date': adjusted_date.strftime("%H:%M %d-%m-%Y %Z"),
                    'tour_guide': review.tour_guide,
                    'author_email': review.author_email,
                    'comments': comments_all
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
                
                review = Reviews.get_by_id(int(reviewID))
                user_tz = timezone('Asia/Singapore')
                adjusted_date = review.review_date.replace(tzinfo=pytz.utc).astimezone(user_tz)

                comment_query = Comments.query(ancestor=review.key).order(Comments.comment_date)
                
                comments_all = comment_query.fetch()
                for comms in comments_all:
                    comms.comment_date = comms.comment_date.replace(tzinfo=pytz.utc).astimezone(user_tz)

                template_values = {
                    'country': review.country,
                    'author': review.author,
                    'location': review.location,
                    'review': review.Review,
                    'rating': review.Rating,
                    'date': adjusted_date.strftime("%H:%M %d-%m-%Y %Z"),
                    'tour_guide': review.tour_guide,
                    'author_email': review.author_email,
                    'comments': comments_all
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

    def post(self):
        user = users.get_current_user()
        reviewID = self.request.get('reviewid')

        if user:
            if reviewID:

                reviewKey = Reviews.get_by_id(int(reviewID)).key
                comment = Comments(parent=reviewKey,
                                   comments = self.request.get('comments'),
                                   comment_author = users.get_current_user().nickname())
                comment.put()
                
                self.redirect('/reviews?reviewid=%s'%reviewID)
            else:
                self.redirect('/reviews')
                
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
        for rev in search_results:
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

            template = jinja_environment.get_template('reviews.html')
            self.response.out.write(template.render(template_values))

    def post(self):
        searchQueryText = self.request.get('search')
        
        self.redirect('/search?query=%s'%searchQueryText)
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', LoginSucessPage),
                               ('/post', PostReview),
                               ('/reviews', ViewReviews),
                               ('/search', SearchResults),
                               ('/delete', DeleteReview),
                               ('/edit', EditReview)],
                              debug=True)

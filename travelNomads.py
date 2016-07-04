import urllib
import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Reviews(ndb.Model):
    author = ndb.StringProperty()
    location = ndb.StringProperty()
    Review = ndb.StringProperty()
    Rating = ndb.IntegerProperty()
    review_date = ndb.DateTimeProperty(auto_now_add=True)
    
    

class MainPage(webapp2.RequestHandler):
    """ Handler for the front page."""

    def get(self):
        user = users.get_current_user()
        
        if user: # signed in
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render())

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
        review = Reviews(author=users.get_current_user.nickname(),
                         location=self.request.get('location'),
                         review=self.request.get('review'), rating=3)
        review.put()
        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
             }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
        
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', LoginSucessPage),
                               ('/post', PostReview)],
                              debug=True)

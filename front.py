import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
  """ Handler for the front page."""
  def get(self):
      template = jinja_environment.get_template('front.html')
      nav_dic = {'Home': 'active', 'Create': 'normal', 'Explore': 'normal', 'My Account':'normal', 'Support': 'normal'}
      nav_list = ['Home','Create','Explore','My Account','Support']
      self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list}))
      
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)

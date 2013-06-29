import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
  """ Handler for the front page."""
  def get(self):
      template = jinja_environment.get_template('home.html')
      nav_dic = {'Home': 'active'}
      nav_list = ['Home','Upload','Album']
      nav_url = {'Home':'home', 'Upload': 'upload', 'Album': 'album'}
      self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
      
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)

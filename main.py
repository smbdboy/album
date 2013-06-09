import urllib
import webapp2
import jinja2
import os
import datetime


from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users

jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# This part for the home page

class Home(webapp2.RequestHandler):
    """ Front page for those logged in """
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            myAccount = 'My Account(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'active',
                    'Create': 'normal',
                    'Explore':'normal',
                    myAccount:'normal',
                    'Support':'normal',
                    'Signout':'normal'}
            nav_list = ['Home',
                    'Create',
                    'Explore',
                    'Support',
                    myAccount,
                    'Signout']
            nav_url = {'Home':'home',
                    'Create': 'create',
                    'Explore':'explore',
                    myAccount:'myaccount',
                    'Support':'support',
                    'Signout':users.create_logout_url("/")}
            template = jinja_environment.get_template('home.html')
            self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
        else:
            self.redirect(self.request.host_url)

class Create(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            myAccount = 'My Account(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'normal',
                    'Create': 'active',
                    'Explore':'normal',
                    myAccount:'normal',
                    'Support':'normal',
                    'Signout':'normal'}
            nav_list = ['Home',
                    'Create',
                    'Explore',
                    'Support',
                    myAccount,
                    'Signout']
            nav_url = {'Home':'home',
                    'Create': 'create',
                    'Explore':'explore',
                    myAccount:'myaccount',
                    'Support':'support',
                    'Signout':users.create_logout_url("/")}
            template = jinja_environment.get_template('create.html')
            self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url, 'upload_url': blobstore.create_upload_url('/upload')}))
        else:
            self.redirect(self.request.host_url)


class Explore(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            myAccount = 'My Account(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'normal',
                    'Create': 'normal',
                    'Explore':'active',
                    myAccount:'normal',
                    'Support':'normal',
                    'Signout':'normal'}
            nav_list = ['Home',
                    'Create',
                    'Explore',
                    'Support',
                    myAccount,
                    'Signout']
            nav_url = {'Home':'home',
                    'Create': 'create',
                    'Explore':'explore',
                    myAccount:'myaccount',
                    'Support':'support',
                    'Signout':users.create_logout_url("/")}
            template = jinja_environment.get_template('explore.html')
            self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
        else:
            self.redirect(self.request.host_url)

class MyAccount(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            myAccount = 'My Account(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'normal',
                    'Create': 'normal',
                    'Explore':'normal',
                    myAccount:'active',
                    'Support':'normal',
                    'Signout':'normal'}
            nav_list = ['Home',
                    'Create',
                    'Explore',
                    'Support',
                    myAccount,
                    'Signout']
            nav_url = {'Home':'home',
                    'Create': 'create',
                    'Explore':'explore',
                    myAccount:'myaccount',
                    'Support':'support',
                    'Signout':users.create_logout_url("/")}
            template = jinja_environment.get_template('myaccount.html')
            self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
        else:
           self.redirect(self.request.host_url)

class Support(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            myAccount = 'My Account(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'normal',
                    'Create': 'normal',
                    'Explore':'normal',
                    myAccount:'normal',
                    'Support':'active',
                    'Signout':'normal'}
            nav_list = ['Home',
                    'Create',
                    'Explore',
                    'Support',
                    myAccount,
                    'Signout']
            nav_url = {'Home':'home',
                    'Create': 'create',
                    'Explore':'explore',
                    myAccount:'myaccount',
                    'Support':'support',
                    'Signout':users.create_logout_url("/")}
            template = jinja_environment.get_template('support.html')
            self.response.out.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
        else:
            self.redirect(self.request.host_url)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            upload_files = self.get_uploads('images')# 'file' is file upload field in the form
            user_picture = Picture(owner = user.user_id(), blob_key = upload_files[0].key())
            db.put(user_picture)
            self.redirect('/serve/%s' % upload_files[0].key())
        else:
            self.redirect(self.request.host_url)

class Serve(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

# Datastore definitions
class Picture(db.Model):
    """Models a person identified by email"""
    owner = db.StringProperty()
    blob_key = blobstore.BlobReferenceProperty()


app = webapp2.WSGIApplication([ ('/home', Home),
                                ('/create', Create),
                                ('/explore', Explore),
                                ('/myaccount', MyAccount),
                                ('/support', Support),
                                ('/serve/([^/]+)?', Serve),
                                ('/upload', UploadHandler)],
                                debug=True)

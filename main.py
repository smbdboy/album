import urllib
import time
import webapp2
import jinja2
import os
import datetime
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.api import images

jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# This part for the home page

class Home(webapp2.RequestHandler):
    """ Front page for those logged in """
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            Signout = 'Signout(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Home':'active'}
            nav_list = ['Home',
                    'Upload',
                    'Album',
                    Signout]
            nav_url = {'Home':'home',
                    'Upload': 'upload',
                    'Album':'album',
                    Signout:users.create_logout_url("/")}
            template = jinja_environment.get_template('home.html')
            self.response.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
        else:
            self.redirect(self.request.host_url)

class BlobStoreUpload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            upload_files = self.get_uploads('picture')  
            blob_infos = upload_files #blob_key is stored in here
            #user may upload more than one file by one form
            for blob_info in blob_infos:
                pic = Picture(owner = user.user_id(), is_in_album = False, blob_key = blob_info.key())
                pic.put()
            time.sleep(0.5) #so after redirect the upload process will has already been finished
            self.redirect('/upload')
        else:
            self.redirect(self.request.host_url)

class Upload(webapp2.RequestHandler): #this upload does not deal with upload form submit only upload
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            Signout = 'Signout(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Upload':'active'}
            nav_list = ['Home','Upload','Album',Signout]
            nav_url = {'Home':'home','Upload': 'upload','Album':'album',Signout:users.create_logout_url("/")}
            # select and display all the pic which does not belong to any album
            pics = Picture.all()
            pics.filter('owner =', user.user_id())
            pics.filter('is_in_album =', False)
            pics = pics.run()
            pic_urls = []
            debug = ''
            for pic in pics:
                pic_urls.append(images.get_serving_url(pic.blob_key))
            template = jinja_environment.get_template('upload.html')
            var = {
                    'info': debug,
                    'nav_dic' : nav_dic,
                    'nav_list':nav_list,
                    'nav_url': nav_url,
                    'blobstore_upload': blobstore.create_upload_url('/blobstore_upload'),
                    'upload_url': 'create',
                    'pics': pic_urls,
                }
            self.response.out.write(template.render(var))
        else:
            self.redirect(self.request.host_url)

class Album(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user: 
            Signout = 'Signout(<em>' + user.nickname() + '</em>)'
            nav_dic = {'Album':'active'}
            nav_list = ['Home',
                    'Upload',
                    'Album',
                    Signout]
            nav_url = {'Home':'home',
                    'Upload': 'upload',
                    'Album':'album',
                    Signout:users.create_logout_url("/")}
            template = jinja_environment.get_template('album.html')
            self.response.write(template.render({'nav_dic' : nav_dic,'nav_list':nav_list, 'nav_url': nav_url}))
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
    owner = db.StringProperty() # identify the owner by user id
    album = db.StringProperty()
    is_in_album = db.BooleanProperty()
    blob_key = blobstore.BlobReferenceProperty()


app = webapp2.WSGIApplication([ ('/home', Home),
                                ('/upload', Upload),
                                ('/blobstore_upload', BlobStoreUpload),
                                ('/album', Album)],
                                debug=True)

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
            blob_infos = self.get_uploads('picture') #get_uploads returns a list of BlobInfo objects
            #user may upload more than one file by one form
            for blob_info in blob_infos:
                pic = Picture(owner = user.user_id(), is_in_album = False, blob_key = blob_info.key(), date=datetime.datetime.now())
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
            pics.filter('is_in_album =', False) # do not show the pics that already belong to some album
            pics.order('date') # put the newest uploaded photo at the end
            pics = pics.run()
            pic_urls = []  # urls are stored into an ordered list
            pic_filenames = {} # pic_filenames is a dic pic_url : pic_name
            pic_keys = {} # a dic storing the pic key for that pic
            debug = ''
            for pic in pics:
                url = images.get_serving_url(pic.blob_key, size=1600, crop=True) # crop the image to have a formated output
                pic_urls.append(url)
                pic_filenames[url] = pic_name(pic.blob_key.filename)
                pic_keys[url] = pic.key()
            template = jinja_environment.get_template('upload.html')
            var = {
                    'info': debug,
                    'pic_filenames': pic_filenames,
                    'pic_keys': pic_keys,
                    'nav_dic' : nav_dic,
                    'nav_list':nav_list,
                    'nav_url': nav_url,
                    'blobstore_upload': blobstore.create_upload_url('/blobstore_upload'),
                    'upload_url': 'create',
                    'pic_urls': pic_urls,
                }
            self.response.out.write(template.render(var))
        else:
            self.redirect(self.request.host_url)

class DeleteAlbum(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user: 
            del_album_key = self.request.POST['album_id']
            album = Album.get(del_album_key)
            pics = Picture.all()
            pics.filter('album =', album)
            if 'album_id_with_pics' in self.request.POST:
                for pic in pics:
                    del_blob(pic.key()) #  delete the the blob
                    pic.delete()
            else:
                for pic in pics:
                    pic.is_in_album = False
                    pic.album = None
                    pic.put()
            album.delete()
            time.sleep(0.5)
            self.redirect('/album') #delet a pic and after delete go to upload page
        else:
            self.redirect(self.request.host_url)

class DeletePicture(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user: 
            del_pickey = self.request.POST['del_pic']
            del_blob(del_pickey) # first, delete the the blob
            del_pic(del_pickey) # then, delete the picture

            time.sleep(0.5)
            self.redirect('/upload') #delet a pic and after delete go to upload page
        else:
            self.redirect(self.request.host_url)

class GenerateAlbum(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            post = self.request.POST
            album = Album(owner = user.user_id(), name = post['album_name'], date = datetime.datetime.now())
            album.put() # put the album into database
            pics = Picture.all()
            pics.filter('owner =', user.user_id())
            pics.filter('is_in_album =', False) # do not show the pics that already belong to some album
            for pic in pics:
                pic.is_in_album = True
                pic.album = album # album is identified by the album id.
                pic.put()
            time.sleep(0.5)
            self.redirect('/album') # redirect to album list
        else:
            self.redirect(self.request.host_url)


class AlbumList(webapp2.RequestHandler):
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
            debug = ''
            template = jinja_environment.get_template('album.html')
            album = Album.all()
            album.filter('owner =', user.user_id())
            album.order('-date')
            albums = album.run()
            cp_albums = album.run()
            access_albums = {}
            for a in cp_albums:
                ins = AccessOfAlbum.all()
                ins.filter('album =', a)
                ins = ins.get()
                if ins:
                    access_albums[a.name] = ins.accessibility
                else:
                    access_albums[a.name] = 'own'

            var = {
                    'info': debug,
                    'nav_dic' : nav_dic,
                    'nav_list':nav_list,
                    'nav_url': nav_url,
                    'albums': albums,
                    'access_albums': access_albums,
                }
            self.response.write(template.render(var))
        else:
            self.redirect(self.request.host_url)

class ShowAlbum(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user: 
            debug = ''
            post = self.request.POST
            album_id = post['album_id']
            album = Album.get(album_id)
            pics = Picture.all()
            pics.filter('album =', album)
            pics.order('-date')
            pics = pics.run()
            pic_urls = []
            pic_names = {}
            for pic in pics:
                url = images.get_serving_url(pic.blob_key)
                pic_urls.append(url)
                pic_names[url] = pic.blob_key.filename
            var = {
                    'info': debug,
                    'pic_urls': pic_urls,
                    'album': album,
                    'pic_names': pic_names,
                }
            template = jinja_environment.get_template('show_album.html')
            self.response.out.write(template.render(var))
        else:
            self.redirect(self.request.host_url)

class AccessAlbum(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user: 
            url = self.request.url
            # last item in url is the key to the album
            album_id = (url.split('/'))[len(url.split('/')) - 1]
            album = Album.get(album_id)
            AOA = AccessOfAlbum.all()
            AOA.filter('album =', album)
            AOA = AOA.run()
            re = ''
            for a in AOA:
                re = a
            AOA = re
            if AOA:
                self.response.out.write(AOA.accessibility)
                if AOA.accessibility == 'public':
                    AOA.accessibility = 'own'
                else:
                    AOA.accessibility = 'public'
                AOA.put()
            else:
                self.response.out.write('aoa does not appear')
                ins = AccessOfAlbum(album=album, accessibility = 'public')
                ins.put()
            #self.response.out.write(url)
            time.sleep(0.5)
            self.redirect('/album') 
        else:
            self.redirect(self.request.host_url)


# Datastore definitions
class Album(db.Model):
    owner = db.StringProperty() # identify the owner by user id
    name = db.StringProperty() # album name
    date = db.DateTimeProperty() # date of creation

class AccessOfAlbum(db.Model):
    album = db.ReferenceProperty(Album)
    accessibility = db.StringProperty()

class Picture(db.Model):
    owner = db.StringProperty() # identify the owner by user id
    album = db.ReferenceProperty(Album) # refer to an album
    is_in_album = db.BooleanProperty()
    date = db.DateTimeProperty() # date of creation
    blob_key = blobstore.BlobReferenceProperty()

# some functions
def pic_name(name): # function to restrict string to a limited length
    if len(name) > 21 :
        name = name[:18] + '...'
    return name

def del_pic (key): # delete the Picture by its unique key
    pic = Picture.get(key)
    pic.delete()
    
def del_blob (key): # delete the pic blob by a pic key
    pic = Picture.get(key)
    pic.blob_key.delete()

class RaspBerry(webapp2.RequestHandler):
    def post(self):
        post = self.request.POST
        message = 'posted messages: --'+post['ip']
        if post['ip']:
            ip = IP(date=datetime.datetime.now(), ip=post['ip'])
            ip.put()
        self.response.write(message)
    def get(self):
        ips = IP.all()
        ips.order('-date') # sort the data by date so the latest update is on top of the page
        ips = ips.run()
        message = 'goted ip from raspberry<br/>'
        for ip in ips:
            message += ip.ip + '@' + str(ip.date) + '<br/>'
        self.response.write(message)

class IP(db.Model):
    date = db.DateTimeProperty() 
    ip = db.StringProperty() 
   
app = webapp2.WSGIApplication([ ('/home', Home),
                                ('/upload', Upload),
                                ('/blobstore_upload', BlobStoreUpload),
                                ('/del_pic', DeletePicture),
                                ('/gen', GenerateAlbum),
                                ('/show_album', ShowAlbum),
                                ('/access_album/.*', AccessAlbum),
                                ('/del_album', DeleteAlbum),
                                ('/raspberry', RaspBerry),
                                ('/album', AlbumList)],
                                debug=True)

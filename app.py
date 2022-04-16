import datetime
from flask import Flask, render_template, request, make_response,jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import random
import time
from progress.bar import Bar
import requests
import os
import sys
from flickrapi import FlickrAPI

#flicker initialization
class Idown:
    api_key = u'17c46cc46051677475500e33ce2a0e18'
    api_secret = u'fd9bcdd95543e079'
    flickr = FlickrAPI(api_key, api_secret)
    SIZES = ["url_o", "url_k", "url_h", "url_l", "url_c"]
    number_objects = 10;
    name_object = ""
    def __init__(self,num_objects,name):
        self.number_objects = num_objects
        self.name_object = name
    def get_photos(self,image_tag):
        extras = ','.join(self.SIZES)
        photos = self.flickr.walk(text=image_tag,  # it will search by image title and image tags
                                extras=extras,  # get the urls for each size we want
                                privacy_filter=1,  # search only for public photos
                                per_page=50,
                                sort='relevance')  # we want what we are looking for to appear first
        return photos
    def get_url(self,photo):
        for i in range(len(self.SIZES)):  # makes sure the loop is done in the order we want
            url = photo.get(self.SIZES[i])
            if url:  # if url is None try with the next size
                return url
    def get_urls(self,image_tag, max):
        photos = self.get_photos(image_tag)
        counter=0
        urls=[]

        for photo in photos:
            if counter < max:
                url = self.get_url(photo)  # get preffered size url
                if url:
                    urls.append(url)
                    counter += 1
                # if no url for the desired sizes then try with the next photo
            else:
                break

        return urls

    #downloader initialization
    def create_folder(self,path):
        if not os.path.isdir(path):
            os.makedirs(path)
    def download_images(self,urls, path):
        self.create_folder(path)  # makes sure path exists
        for url in urls:
            image_name = url.split("/")[-1]
            image_path = os.path.join(path, image_name)

            if not os.path.isfile(image_path):  # ignore if already downloaded
                response=requests.get(url,stream=True)

                with open(image_path,'wb') as outfile:
                    outfile.write(response.content)

    def download(self):
        print('Getting urls for', self.name_object)
        urls = self.get_urls(self.name_object, self.number_objects)
        print('Downloading images for', self.name_object)
        path = os.path.join('data', self.name_object)
        self.download_images(urls, path)



def create_app():
    app = Flask(__name__)
    api = Api(app)
    #set flask api
    client = MongoClient("mongodb+srv://wolf_comos:021115@microblogcluster.mv4br.mongodb.net/test")
    app.db = client.TheHelp
    # connect to Mongodb database
    class Helloworld(Resource):
        def get(self):
            return {"data" : "Hello world"}

    api.add_resource(Helloworld,"/helloworld")

    # flickr api initialization


    key = False
    @app.route("/", methods=["GET","POST"])
    def index():
    #判定是否又cookie
        #print([e for e in app.db.entries.find({})])
        if request.method == "POST":
            entry_user = request.cookies.get("name")
            entry_content = request.form.get("content")
            image_x = Idown(2, entry_content)
            image_x.download();
            print(entry_content)
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            random.seed(8)
            post_id = str(random.random()*(10^8))
            print(post_id)
            app.db.entries.insert({"content": entry_content,
                                   "date": formatted_date,
                                   "user": entry_user,
                                   "post_id": post_id})
            #post_id = random.seed(8)
            # one_post = app.db.post
            # one_post.insert({"post_id":post_id})

        entries_with_date = [
            (
                entry["user"],
                entry["content"],
                entry["date"],
                entry["post_id"]
            )
            for entry in app.db.entries.find({})
        ]
        return render_template("index.html", entries=entries_with_date)
    return app;
if __name__ == "__main__":
    create_app()

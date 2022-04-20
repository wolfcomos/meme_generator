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
from PIL import Image, ImageDraw, ImageFont

file_list = []
dir_name = ""
def image_processor(entry_text,address):
    old_img = Image.open(address)
    X, Y = old_img.size
    new_image = old_img.resize((300, 300), Image.ANTIALIAS).transpose(Image.ROTATE_90)
    draw = ImageDraw.Draw(new_image)
    newfont = ImageFont.truetype('simkai.ttf', 20)
    draw.text((40, 150), entry_text, font=newfont, fill="black")
    new_image = new_image.save("new.jpeg")
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
        path = './static'
        path = os.path.join(path, self.name_object)
        self.download_images(urls, path)

def create_file_list(dir_name):
    list_files = []
    for root, dirs, files in os.walk('./static/'+dir_name+'/',topdown=False):
        for name in files:
            list_files.append(os.path.join(root, name))
    return list_files
def create_app():
    app = Flask(__name__)
    api = Api(app)
    #set flask api
    client = MongoClient("")
    app.db = client.Microblog.entries
    # connect to Mongodb database
    class Helloworld(Resource):
        def get(self):
            return {"data" : "Hello world"}

    api.add_resource(Helloworld,"/helloworld")

    # flickr api initialization


    key = False
    @app.route("/", methods=["GET","POST"])
    def index():
        global dir_name;
        #print([e for e in app.db.entries.find({})])
        global file_list
        if request.method == "POST":
            entry_content = request.form.get("content")
            dir_name = entry_content
            image_x = Idown(2, entry_content)
            image_x.download()
            print(entry_content)
            file_list = create_file_list(entry_content)
            app.db.entries.insert({"content": entry_content})
        return render_template("index.html", entries=file_list)

    @app.route("/text_generator/<picture_name>", methods=["GET", "POST"])
    def text_generate(picture_name):
        print("soooo cooolll")
        print(picture_name)
        img_path = load_image(picture_name)
        if request.method == "POST":
            meme_text = request.form.get("content_meme")
            image_processor(meme_text,img_path)
        return render_template("meme_text.html", entry_img=img_path, page_index=picture_name)

    @app.route("/new_image", methods=["GET", "POST"])
    def image_new():
        if request.method == "GET":
            new_image_path = './static/'+dir_name+'/new.jpeg'
            return render_template("new_image.html", entry_image=new_image_path, dir_name=dir_name)

    return app

def load_image(pic_name):
    index_name = int(pic_name)
    img_path = file_list[index_name]
    print(img_path)
    return img_path


if __name__ == "__main__":
    create_app()

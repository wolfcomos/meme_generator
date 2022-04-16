import os
import time
from progress.bar import Bar
import requests
import os
import sys
import time
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

    #testing


if __name__ == "__main__":
    object = Idown(2,"face")
    object.download();


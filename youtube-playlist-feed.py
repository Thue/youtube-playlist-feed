import urllib2
import json
from pyatom import AtomFeed
import datetime
from dateutil import parser
import re
import mod_python

def index(req):
   key = "ReplaceMe" #EDIT THIS LINE
   if key == "ReplaceMe":
      req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
      return "Before this script can be used, you need to edit this script to set 'key = \"...\"' to your own Google API key. Get your personal key from https://developers.google.com/api-client-library/python/guide/aaa_apikeys ."

   #check playlistId GET argument
   playlistId = req.form.getfirst('playlistId', None)
   if playlistId == None:
      req.status = mod_python.apache.HTTP_BAD_REQUEST
      return "The playlistId GET argument is required"
   valid_playlist = re.compile("\A\w+\Z");
   if not valid_playlist.match(playlistId):
      req.status = mod_python.apache.HTTP_BAD_REQUEST
      return "Invalid playlistId argument. The playlistId may only contain the characters [a-zA-Z0-9_]."

   #Get info about playlist
   pl_info_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet&id="+playlistId+"&key="+key+"&maxResults=50"
   try:
      response = urllib2.urlopen(pl_info_url)
      js = response.read()
   except urllib2.HTTPError, error:
      js = error.read()
      req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
      if js is None:
         gerror = ""
      else:
         gerror = " Error returned by googleapis.com: " + js;
      return "Failed to fetch playlist info from Google. Your Google developer key is invalid, or Google is down."+gerror
   decoded = json.loads(js)
   if len(decoded["items"]) == 0:
      req.status = mod_python.apache.HTTP_BAD_REQUEST
      return "No playlist with that playlistID found"
   channelTitle = decoded["items"][0]["snippet"]["channelTitle"]
   playlistTitle = decoded["items"][0]["snippet"]["title"]

   #Get videos in playlist
   items = []
   base_url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId="+playlistId+"&key="+key+"&maxResults=50";
   url = base_url
   for rounds in range (0, 50):
      try:
         response = urllib2.urlopen(url)
         js = response.read()
      except urllib2.HTTPError, error:
         js = error.read()
         req.status = mod_python.apache.HTTP_INTERNAL_SERVER_ERROR
         if js is None:
            gerror = ""
         else:
            gerror = " Error returned by googleapis.com: " + js;
            return "Failed to fetch playlist items from Google. Your Google developer key is invalid, or Google is down"
      decoded = json.loads(js)
      items = items + decoded["items"]
      if 'nextPageToken' in decoded:
         url = base_url+"&pageToken="+decoded["nextPageToken"]
      else:
         break

   #generate feed
   feed = AtomFeed(title=channelTitle+": " + playlistTitle,
                   url="https://www.youtube.com/playlist?list="+playlistId)
   #add items to feed
   for episode in items:
      s = episode["snippet"]
      #For whatever reason, YouTube includes private videos in the results. Which you cannot watch. Remove them.
      if s["title"] != "Private video":
         feed.add(title=s["title"],
                  url="https://youtube.com/watch?v="+s["resourceId"]["videoId"],
                  published=parser.parse(s["publishedAt"]),
                  updated=parser.parse(s["publishedAt"]),
                  author=channelTitle,
                  )

   return feed.to_string()

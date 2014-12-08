youtube-playlist-feed
=====================

An Apache webserver mod_python script to create an Atom feed from a YouTube
playlist. An Atom feed is a type of web feed similar to RSS, which can
be used for web syndication, e.g. in a feed reader such as e.g. "feeder".

Usage
=====================

* Get a Google API key, to allow you to query Google's YouTube API.
* Insert your API key at the top of youtube-playlist-feed.py (edit the line 'key = "ReplaceMe"')
* Upload to your webroot
* Enable mod_python on your Apache ( http://modpython.org/ )
* In your browser, find the YouTube playlist you want to create an
  Atom feed for. For example:
  https://www.youtube.com/playlist?list=PLC9578E9DD2663C66
* From that URL, extract the playlistId ("PLC9578E9DD2663C66" in this
  case)
* if you put the script at
  http://www.example.com/youtube-playlist-feed.py , an Atom feed with
  the latest entries for the playlist is will be generated every time
  you visit
  http://www.example.com/youtube-playlist-feed.py?playlistId=PLC9578E9DD2663C66

Notes
=====================

Does not cache queries, so inefficient if used with many simultaneous
users.
## Automatic Album Face Swap

Simple python web app that can replace a face on an album cover with a second face.
Album cover is retrieved using Deezer API based on a Deezer album_id, that can be found on an album page url:
ex: [http://www.deezer.com/album/238939](http://www.deezer.com/album/238939)

![screenshot](https://github.com/xbenji/deezer-album-face-swap/blob/master/screenshot.jpg)

The app is just wrapping faceswap algorithm from [Matthew Earl](https://github.com/matthewearl/faceswap) as detailed in [Switching Eds blog post](http://matthewearl.github.io/2015/07/28/switching-eds-with-python/).

Usage:
run server.py and connect to localhost 

Requirements:
- dlib (http://dlib.net) + Python bindings
- OpenCV. 

You'll also need to obtain the trained model [from
sourceforge](http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2).
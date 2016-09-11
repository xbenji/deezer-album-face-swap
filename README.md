## Automatic Album Face Swap

Simple python web app that can replace a face on an album cover with a second face.

The app is just wrapping a faceswap algorithm from [Matthew Earl](https://github.com/matthewearl/faceswap) as detailed in [Switching Eds blog post](http://matthewearl.github.io/2015/07/28/switching-eds-with-python/).

Requirements:
- dlib (http://dlib.net) + Python bindings
- OpenCV. 

You'll also need to obtain the trained model [from
sourceforge](http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2).
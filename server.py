import SocketServer

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler

import hashlib
import time
import cgi
import cv2

import numpy
import faceswap as fs

import urllib, json, urlparse, re

from os import curdir, sep, mkdir


PORT = 8000

class MyRequestHandler (BaseHTTPRequestHandler) :

    def _get_file(self, form, form_file, job_path):
        data = form[form_file].file.read()
        path = job_path + sep + form[form_file].filename
        open(path, "wb").write(data)
        return path

    def _faceswap(self, album, face, job_path, use_jaws=False):

        align_points = fs.get_align_points(use_jaws)

        print "detecting faces..."
        im1, landmarks1 = fs.read_im_and_landmarks(album)
        im2, landmarks2 = fs.read_im_and_landmarks(face)

        # cv2.imwrite('tmp/output-lm1.jpg', annotate_landmarks(im1, landmarks1))
        # cv2.imwrite('tmp/output.lm2.jpg', annotate_landmarks(im2, landmarks2))

        print "aligning points..."
        M = fs.transformation_from_points(landmarks1[align_points], landmarks2[align_points])

        print "create alpha masks...",
        mask = fs.get_face_mask(im2, landmarks2, use_jaws)
        warped_mask = fs.warp_im(mask, M, im1.shape)
        combined_mask = numpy.max([fs.get_face_mask(im1, landmarks1, use_jaws), warped_mask], axis=0)

        print "warping images...",
        warped_im2 = fs.warp_im(im2, M, im1.shape)
        warped_corrected_im2 = fs.correct_colours(im1, warped_im2, landmarks1)

        output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask

        result = job_path + sep + 'output.jpg'
        cv2.imwrite(result, output_im)
        return result

    def do_GET(self) :

        # path: /cover_url/<alb_id>
        # deezer api proxy to get cover image url for an alb_id
        if None != re.search('/cover_url/*', self.path):
            alb_id = self.path.split('/')[-1]
            response = urllib.urlopen('http://api.deezer.com/album/%s' % alb_id)
            data = json.loads(response.read())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data))
            return

        # path: /swap/<job_id>
        # display a job_id output
        if None != re.search('/swap\/.*', self.path):
            job_id = self.path.split('/')[-1]
            print job_id
            img = "../swap_{}/output.jpg".format(job_id)

            self.send_response(200)
            self.send_header("Content-type:", "text/html")
            self.end_headers()
            self.wfile.write("<html><img src='%s'></img></html>" % img)
            return

        if self.path == "/" :
            self.path="/index.html"

        try:
            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()

        except Exception as e:
            print str(e)
        
        return


    def do_POST(self):

        if self.path == "/faceswap" :
            length = int(self.headers['content-length'])
            #print length
            if length > 10000000:
                print "file to big"
                read = 0
                while read < length:
                    read += len(self.rfile.read(min(66556, length - read)))
                self.wfile.write("file to big")
                return
            else:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                             'CONTENT_TYPE':self.headers['Content-Type'],
                             })

                # path
                job_id = hashlib.sha224(str(time.time())).hexdigest()[:8]
                job_path = './swap_{}'.format(job_id)
                mkdir(job_path)

                # get face
                face_filename = self._get_file(form, 'facefile', job_path)

                # get album
                album_filename = ''
                if form['albid'].value != None:
                    alb_id = str(form['albid'].value)
                    response = urllib.urlopen('http://api.deezer.com/album/%s' % alb_id)
                    data = json.loads(response.read())
                    alb_cover_url = data['cover_big']
                    album_filename, headers = urllib.urlretrieve(alb_cover_url, "./%s/alb-%s.jpg" % (job_path, alb_id))
                else:
                    album_filename = self._get_file(form, 'albumfile')

                try:
                    img = self._faceswap(album_filename, face_filename, job_path)

                    # redirect to job_id result page
                    self.send_response(301)
                    self.send_header('Location','/swap/{}'.format(job_id))
                    self.end_headers()

                except Exception as e:
                    self.send_response(200)
                    self.send_header("Content-type:", "text/html")
                    self.end_headers()
                    self.wfile.write("<html><pre>ERROR: {}</pre></html>".format(str(e)))


if __name__ == '__main__':

    server = HTTPServer(("localhost", PORT), MyRequestHandler)

    print "serving at port", PORT
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
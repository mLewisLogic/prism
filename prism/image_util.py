#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

from cStringIO import StringIO
import hashlib
import Image
import ImageFile
ImageFile.MAXBLOCK = 1000000 # default is 64k (overcome 'Suspension not allowed here' bug in JPEG decoder)
import urllib2



def load_image_from_string(s):
    """Loads a PIL image from a string"""
    try:
        return Image.open(StringIO(s))
    except IOError, e:
        log.error(e)
        return None

def load_image_from_file(filename):
    """Loads a PIL image from a file"""
    return Image.open(filename)

def load_image_from_url(url):
    """Loads a PIL image from a url"""
    try:
        image_string = urllib2.urlopen(url).read()
        return load_image_from_string(image_string)
    except urllib2.HTTPError, e:
        log.error(e)
        return None


class ImageHelper(object):
    """Helper methods for images"""
    def __init__(self, image):
        """Start with an object as the focus of this class"""
        self.image = image

    def md5_hash(self):
        """Gets the md5 hash for this image"""
        return unicode(hashlib.md5(self.image.tostring()).hexdigest())

    def to_jpeg_string(self, params={}):
        """Opens an image file and returns a jpeg binary string representation"""
        # Set default encoding params (but allow overrides)
        encoding_params = {
            'quality': 90,
            'optimize': True,
        }
        encoding_params.update(params)
        # Fix the image if it's not RGB
        if self.image.mode != u'RGB':
            self.image = self.image.convert(u'RGB')
        # Encode the new image to a string buffer and return 
        out_bytes = StringIO()
        self.image.save(out_bytes, u'JPEG', **params)
        return out_bytes.getvalue()

    def to_png_string(self, params={}):
        """Opens an image file and returns a png binary string representation"""
        # Set default encoding params (but allow overrides)
        encoding_params = {
            'optimize': True,
        }
        encoding_params.update(params)
        # Encode the new image to a string buffer and return 
        out_bytes = StringIO()
        self.image.save(out_bytes, u'PNG', **params)
        return out_bytes.getvalue()

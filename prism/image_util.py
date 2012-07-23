#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

from cStringIO import StringIO
import ExifTags
import hashlib
import Image
import ImageFile
import urllib2

# PIL's Error "Suspension not allowed here" work around:
# s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
ImageFile.MAXBLOCK = 1024*1024



def load_image_from_string(s):
    """Loads a PIL image from a string"""
    try:
        image = Image.open(StringIO(s))
        return ImageHelper(image).fix_rotation()
    except IOError, e:
        log.error(e)
        return None

def load_image_from_file(filename):
    """Loads a PIL image from a file"""
    image = Image.open(filename)
    return ImageHelper(image).fix_rotation()

def load_image_from_url(url):
    """Loads a PIL image from a url"""
    try:
        image_string = urllib2.urlopen(url).read()
        image = load_image_from_string(image_string)
        return ImageHelper(image).fix_rotation()
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
            'quality': 95,
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

    def fix_rotation(self):
        """
        Turns EXIF rotation into a physical rotation (doesn't clear the rotation EXIF!)
        see: http://stackoverflow.com/questions/1606587/how-to-use-pil-to-resize-and-apply-rotation-exif-information-to-the-file
        """
        # Get the key for the 'Orientation' EXIF property
        for orientation_key in ExifTags.TAGS.iterkeys():
            if ExifTags.TAGS[orientation_key] is 'Orientation': break

        # Get the EXIF orientation value from our image
        orientation = self.image._getexif().get(orientation_key)

        # Perform our rotation
        if orientation is 1: # Horizontal (normal)
            image = self.image.copy()
        elif orientation is 2: # Mirrored horizontal
            image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation is 3: # Rotated 180
            image = self.image.transpose(Image.ROTATE_180)
        elif orientation is 4: # Mirrored vertical
            image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation is 5: # Mirrored horizontal then rotated 90 CCW
            image = self.image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation is 6: # Rotated 90 CW
            image = self.image.transpose(Image.ROTATE_270)
        elif orientation is 7: # Mirrored horizontal then rotated 90 CW
            image = self.image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation is 8: # Rotated 90 CCW
            image = self.image.transpose(Image.ROTATE_90)
        else:
            pass

        return image

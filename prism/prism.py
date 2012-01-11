#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

from boto.s3.connection import S3Connection

from . import image_util



DEFAULT_IMAGE_FORMAT = u'JPEG'

class Connection(object):
    """Enclosing object through which the system is managed"""

    def __init__(self, s3_connection, bucket_name, bucket_url):
        """Set up the AWS creds and bucket details"""
        self.s3 = s3_connection
        self.bucket_name = bucket_name
        self.bucket_url = bucket_url

    @property
    def bucket(self):
        """Get the S3 bucket being used by this manager"""
        if not hasattr(self, '_bucket'):
            self._bucket = self.s3.get_bucket(self.bucket_name)
        return self._bucket

    def save_image(self, key_name, image, format):
        """Saves this image to an S3 bucket, using a specified file format"""
        log.debug(u'Saving key [{key_name} to {bucket}]'.format(
            key_name=key_name,
            bucket=self.bucket))
        key = self.bucket.new_key(key_name)
        format = format.upper()
        if format == u'JPEG':
            image_str = image_util.ImageHelper(image).to_jpeg_string()
            key.set_metadata('Content-Type', 'image/jpeg')
        elif format == u'PNG':
            image_str = image_util.ImageHelper(image).to_png_string()
            key.set_metadata('Content-Type', 'image/png')
        else:
            log.error(u'{0} is not a supported image format'.format(format))
            return
        return key.set_contents_from_string(image_str)

    def get_collection_manager(self, *args, **kwargs):
        """Gets a collection manager stemming from this connection"""
        return CollectionManager(self, *args, **kwargs)



class CollectionManager(object):
    """Management object through which collections of images are processed using the same settings.
    The collection_spec dictates the functionality that an instance will provide.
    
    Parameters (with examples):
    key_prefix=u'users/' # Allows "foldering" of different collections within the same bucket
    format=u'JPEG', # format to save original and derivatives in
    derivative_specs=[ # A list of specs to create derivative images
        {
            'filters': [ThumbnailFilter(120, 80)], # chained list of filters to apply
            'key_suffix': u'(120x80)', # suffix to apply to the key, identifying this derivative
        },
        {
            'filters': [ThumbnailFilter(20, 10)],
            'key_suffix': u'(20x10)',
        },
    ]
    blacklist=[ # Blacklist of md5 hashes to ignore incoming images of
        u'917aa09622f73d57a50294dde50cfdc8',
        u'404b31849f87463d1b51284a0a1c6b65',
        u'59610c7d0716126dc89c299bb92e4ca8',
        u'49f83104c9a168a633314f64723ee7a5',
    ]
    
    """
    def __init__(self, connection, key_prefix=u'', format=DEFAULT_IMAGE_FORMAT, derivative_specs=[], blacklist=[]):
        """Stash the parameters for use on individual processing"""
        self.connection = connection
        self.key_prefix = key_prefix
        self.format = format
        self.derivative_specs = derivative_specs
        self.blacklist = blacklist

    def process_image_string(self, image_string):
        """Process an image string"""
        image = image_util.load_image_from_string(image_string)
        return self.process_image(image)

    def process_image_url(self, image_url):
        """Process an image url"""
        image = image_util.load_image_from_url(image_url)
        return self.process_image(image)

    def process_image_file(self, image_file):
        """Process an image file"""
        image = image_util.load_image_from_file(image_file)
        return self.process_image(image)

    def process_image(self, image):
        """Process this image according to this collection's spec"""
        # Make sure we're playing with a valid image
        if not image:
            log.error(u'image is invalid: {0}'.format(image))
            return None
        # Get the md5 hash of the original image. We'll use this as the base s3 key.
        image_hash = image_util.ImageHelper(image).md5_hash()
        # Make sure this isn't in the blacklist
        if image_hash in self.blacklist:
            log.debug(u'image found in blacklist: {0}'.format(image_hash))
            return None
        # Store the original
        key_prefix = u'{prefix}{image_hash}'.format(
            prefix=self.key_prefix, image_hash=image_hash)
        self.connection.save_image(key_prefix, image, self.format)
        # Process each requested derivative
        for derivative_spec in self.derivative_specs:
            self._save_derivative_image(key_prefix, image, derivative_spec)
        # Return the image hash used
        return image_hash

    def get_url(self, image_hash):
        return u'{bucket_url}{key_prefix}{image_hash}'.format(
            bucket_url=self.connection.bucket_url, key_prefix=self.key_prefix, image_hash=image_hash)

    def get_image(self, image_hash):
        url = self.get_url(image_hash)
        return image_util.load_image_from_url(url)

    def _save_derivative_image(self, base_key, image, spec):
        """Generates and stores the derivative based upon a spec"""
        derivative_image = self._apply_image_filters(image, spec['filters'])
        derivative_key = u'{base_key}{suffix}'.format(
            base_key=base_key, suffix=spec.get('key_suffix', u''))
        self.connection.save_image(derivative_key, derivative_image, self.format)

    def _apply_image_filters(self, image, filters=[]):
        """Creates a derivative image from an original using a filter chain (first-to-last)"""
        derivative = image
        for filter in filters:
            derivative = filter(derivative)
        return derivative

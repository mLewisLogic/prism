#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

import Image



"""
ThumbnailFilter
===============

This allows thumbnailing of an image, given desired width and height.
If both width and height are set, the aspect ratio is fixed and cropping
  will be done to satisfy the output requirements.
#If just width or height are set, the original aspect ratio will be maintained
#  and the the image will be scaled to fit the requested dimension.
"""


class ThumbnailFilter(object):
    """Takes in an image and returns a thumbnailed version"""

    def __init__(self, width=None, height=None):
        """Set up filter details"""
        assert width or height, u'width or height, or both, must be set'
        self.width = width
        self.height = height

    def __call__(self, image):
        """Process the incoming image and return the derivative."""
        # Get ratio info so that we can intelligently crop
        img_ratio = float(image.size[0]) / float(image.size[1])
        new_ratio = float(self.width) / float(self.height)

        if img_ratio < new_ratio:
            # Original is taller than what we want, cut it's height
            new_height = float(image.size[0]) / new_ratio
            crop_dims = (
                0,
                int((image.size[1] / 2) - (new_height / 2)),
                image.size[0] - 1,
                int((image.size[1] / 2) + (new_height / 2)))
        else:
            # Original is wider than what we want, cut it's width
            new_width = float(image.size[1]) * new_ratio
            crop_dims = (
                int((image.size[0] / 2) - (new_width / 2)),
                0,
                int((image.size[0] / 2) + (new_width / 2)),
                image.size[1] - 1)
        return image.crop(crop_dims).resize((self.width, self.height), Image.ANTIALIAS)

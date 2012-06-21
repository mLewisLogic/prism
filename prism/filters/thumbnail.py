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

    def __init__(self, width=None, height=None, max_ratio=None):
        """Set up filter details
        width: The image width to adjust for
        height: The image height to adjust for
        max_ratio: The maximum h:w or w:h ratio we'll tolerate before cropping, >= 1
        """
        assert width or height, u'width or height, or both, must be set'
        self.width = width
        self.height = height
        if max_ratio:
            assert max_ratio >= 1.0, u'max_ratio covers both h:w and w:h, must be greater than 1.0'
        self.max_ratio = max_ratio

    def __call__(self, image):
        """Process the incoming image and return the derivative."""
        log.debug(u"Processing thumbnail filter (w:{width}, h:{height}, maxr:{max_ratio})".format(
            width=self.width,
            height=self.height,
            max_ratio=self.max_ratio
        ))
        current_ratio = float(image.size[0]) / float(image.size[1]) # PIL size is (w, h)
        log.debug(u"Original image: (w:{width}, h:{height}, r:{ratio})".format(
            width=image.size[0],
            height=image.size[1],
            ratio=current_ratio
        ))

        # Calculate our new ratio
        target_ratio = current_ratio
        if self.width and self.height:
            target_ratio = float(self.width) / float(self.height)
        if self.max_ratio:
            if target_ratio > 1.0:
                target_ratio = min(target_ratio, self.max_ratio)
            else:
                target_ratio = max(target_ratio, 1.0 / self.max_ratio)

        # If the ratios are different, make a cropping adjustment
        if current_ratio != target_ratio:
            if current_ratio < target_ratio:
                # Original is taller than what we want, cut it's height
                new_height = float(image.size[0]) / target_ratio
                crop_dims = (
                    0,
                    int((image.size[1] / 2) - (new_height / 2)),
                    image.size[0] - 1,
                    int((image.size[1] / 2) + (new_height / 2)))
            else:
                # Original is wider than what we want, cut it's width
                new_width = float(image.size[1]) * target_ratio
                crop_dims = (
                    int((image.size[0] / 2) - (new_width / 2)),
                    0,
                    int((image.size[0] / 2) + (new_width / 2)),
                    image.size[1] - 1)
            log.debug(u"Cropping ({0})".format(crop_dims))
            image = image.crop(crop_dims)

        # Figure out what our target height and width will be
        if self.width and self.height:
            target_width = self.width
            target_height = self.height
        elif self.width:
            target_width = self.width
            target_height = int(self.width / target_ratio)
        elif self.height:
            target_width = int(self.height * target_ratio)
            target_height = self.height
        else:
            assert False, u"How did you get here?"

        # Resize the image, with AA on
        log.debug(u"Resizing (w:{width}, h:{height})".format(
            width=target_width,
            height=target_height
        ))
        return image.resize((target_width, target_height), Image.ANTIALIAS)

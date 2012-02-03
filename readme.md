# prism

Python library to process images and store the results to Amazon S3. Originally developed to power [Fondu](http://fondu.com).

Philosophy:

* Assume nothing about your data models
* Use the md5 hash of images as keys, avoiding duplicate images and sensitive filenames.

## Usage

    # Imports
    from boto.s3.connection import S3Connection
    import prism

    # Construct an s3 connection client
    s3_conn = S3Connection('YOUR_ACCESS_KEY_ID', 'YOUR_SECRET_ACCESS_KEY')

    # Build a Prism connection object around the s3 connection
    prism_conn = prism.Connection(s3_conn, 'img.example.com', 'http://img.example.com/')

    # Build a processing spec
    spec = {
        'key_prefix': u'users/',
        'format': u'JPEG',
        'derivative_specs': [
            {
                'filters': [prism.filters.ThumbnailFilter(60, 60)],
                'key_suffix': u'-small',
            },
        ],
    }

    # Get the Prism collection manager using this spec
    user_image_manager = prism_conn.get_collection_manager(**spec)

    # Now process images
    image_url = u'http://3.bp.blogspot.com/_xs4Qi1Qk2Ck/TKH76M7UaaI/AAAAAAAADXc/56rKShHiK1M/s1600/hot-dog-mustard-small.jpg'
    image_hash = user_image_manager.process_image_url(image_url)

    # Save the image_hash to your db for later retrieval

    # Get the S3 url for this just-saved image
    url = user_image_manager.get_url(image_hash)

    # A derivative with suffix 'small' was created too
    url_small = u'{url}-small'.format(url=url)


## Spec options

### key_prefix

If present, all keys will be prefixed with this string. Useful for categorizing or foldering different groups of images within the same S3 bucket.

### format

Output format of the images. Options are JPEG or PNG. Defaults to JPEG.

### derivative_specs

A list of derivative images to create from the original. Each derivative spec has parameters as follows:

#### filters

A list of filters to run the original image through to produce the derivative. Works like a processing chain, and runs first to last.

#### key_suffix

A suffix to give each image created from this derivative spec. Used for retrieving this derivative image once you have the url for the original

### blacklist

A list of unicode md5 hashes to blacklist. Useful for "banning" certain images, regardless of filename.
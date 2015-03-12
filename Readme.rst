redditcurl
==========

redditcurl is a small tool to download the pages you have saved on Reddit.
redditcurl can handle:

* Direct image links
* imgur links and albums
* tumblr posts
* RedditBooru galleries

Installation
------------

redditcurl is available on the `Python Package Index <https://pypi.python.org/pypi/redditcurl/>`_
. You can install it via ``pip install redditcurl``. 
If you are installing from sources instead, you can install it by running ``python setup.py build install``.

Requirements
------------

Outside standard library, redditcurl requires:

* ``requests``
* ``praw``
* ``beautifulsoup4``

Setuptools should automatically install these while installing redditcurl.

Usage
-----

To be able to access your saved images, redditcurl requires your username and password. You also need to tell it where the images should be saved. ::

    % redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images

By default, redditcurl will use 5 processes to process the links and download the images.
If you want to disable multiprocessing, or use more processes, you can pick the number of processes with `-c` or `--processes`.

Also by default, redditcurl will give names to the downloaded images, based on the titles of the reddit submissions. If you want to simply keep the names of the downloaded files, you can use `-n` or `--notitles`.

So for example, if you want redditcurl to download your saved images, and store them at `/home/karmanaut/images` without using their titles, and use 10 processes while downloading, you can do::

    % redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images -c 10 -n

If you want redditcurl to remove the images from your saved images as it downloads them, you can use `-r` or `--remove`. Note that redditcurl keeps track of the images that have been downloaded, and will not re-download them the next time it is run, so you should not need to use this flag.

Finally, redditcurl will print out some messages while it runs, including some warnings about failed downloads, and a total count of downloaded and failed images. If you don't want any output, you can use `-s` or `--silent`.

For example, if you want redditcurl to download the images, without using multiprocessing, print nothing while running, and remove the saved images if the downloads succeed, you can do::

    % redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images -c 1 -s -r

Importing
---------

redditcurl can be easily imported into your project.

    >>> from redditcurl import manager
    >>> my_image = "http://i.imgur.com/gUQnp73.gif"
    >>> save_path = "/home/user/images"
    >>> manager.manage_download(my_image, save_path)
    ('http://i.imgur.com/gUQnp73.gif', True)

`redditcurl.manage_download` will pick the correct function and download the image for you.
When download finishes, it will return a tuple, contaning the url and `True` if the download succeeded, `False` otherwise.

Extending
---------

Adding support for new websites to redditcurl is easy. You will need to write a python package that provides two functions:

``match(url)``
  Accepts a string 'url', and returns True if the package can download this image, False otherwise.

``download(url, path, filename="")``
  Accepts 3 strings; 'url', the image that will be downloaded, 'path', the directory where the downloaded image will be saved, and 'filename', the name that should be given to this file. Note that filename can be an empty string, in which case the downloader should keep the name of the file as it is on the website. Also keep in mind that filename will not contain the extension of the file, the downloader should add the extension.

Place this package or file into ``redditcurl/websites``, and edit ``redditcurl/websites/__init__.py`` to import this new package and add it into ``__all__``.

Licensing
---------

redditcurl is licensed with GPLv3. Please see the file `COPYING` for details.

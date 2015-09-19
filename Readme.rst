redditcurl
==========
    
.. image:: https://travis-ci.org/SeriousBug/redditcurl.svg?branch=master
   :target: https://travis-ci.org/SeriousBug/redditcurl

.. image:: https://coveralls.io/repos/SeriousBug/redditcurl/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/SeriousBug/redditcurl?branch=master


redditcurl is a small tool to download the pages you have saved on Reddit.
redditcurl can handle:

* Direct image links
* imgur links and albums
* Gfycat links
* tumblr posts
* Deviantart submissions
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

To start using redditcurl, simply call it with a save directory::

    % redditcurl -d /home/karmanaut/images
    Please visit https://www.reddit.com/api/v1/authorize/?state=... to authorize access to your account history.

Redditcurl will print an authorization URL for you. Visit that and allow redditcurl to access your history.
Once you accept the authorization, you will be redirected to a page. Copy the authorization code you are given, and paste it into redditcurl, and you are done.

By default, redditcurl will use 20 processes to process the links and download the images.
If you want to disable multiprocessing, or use more processes, you can pick the number of processes with `-c` or `--processes`.

Also by default, redditcurl will give names to the downloaded images, based on the titles of the reddit submissions. If you want to simply keep the names of the downloaded files, you can use `-n` or `--notitles`.

So for example, if you want redditcurl to download your saved images, and store them at `/home/karmanaut/images` without using their titles, and use 10 processes while downloading, you can do::

    % redditcurl -d /home/karmanaut/images -c 10 -n

If you want redditcurl to remove the images from your saved images as it downloads them, you can use `-r` or `--remove`. Note that redditcurl keeps track of the images that have been downloaded, and will not re-download them the next time it is run, so you should not need to use this flag.

Finally, redditcurl will print out some messages while it runs, including some warnings about failed downloads, and a total count of downloaded and failed images. If you don't want any output, you can use `-s` or `--silent`.

For example, if you want redditcurl to download the images, without using multiprocessing, print nothing while running, and remove the saved images if the downloads succeed, you can do::

    % redditcurl -d /home/karmanaut/images -c 1 -s -r

Configuring
-----------

You can set up a configuration file instead of setting everything up with command-line flags. This configuration file should be located at `$XDG_CONFIG_HOME/redditcurl`, or `.config/redditcurl` if that variable is not set. A sample configuration file is below::

    [redditcurl]
    savedir = /home/karmanaut/Pictures
    processes = 10
    subfolders = true

You can set up all command line options in the configuration file as well, simply use their long names without the dashes. Note that no variable expansion or globbing is done on savedir, so it must be set to an absolute path.

Even if you don't create a configuration file yourself, redditcurl will write one the first time it is run.
    
Importing
---------

redditcurl can be easily imported into your project.

    >>> from redditcurl import manager
    >>> my_image = "http://i.imgur.com/gUQnp73.gif"
    >>> save_path = "images/"
    >>> file_name = "funny_picture"
    >>> manager.manage_download(my_image, save_path, file_name)
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

Place this package or file into ``redditcurl/websites``, and edit ``redditcurl/websites/__init__.py`` to import this new package and add it into ``downloaders`` list.

Licensing
---------

redditcurl is licensed with GPLv3. Please see the file `COPYING` for details.

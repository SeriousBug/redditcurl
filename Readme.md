# redditcurl

redditcurl is a small tool to download the pages you have saved on Reddit.
redditcurl can handle:

* Direct image links
* imgur links and albums
* tumblr posts
* RedditBooru galleries

redditcurl is inspired from Adrian Espinosa (aesptux)'s download-reddit-saved-images script.
His script supports more websites, and can be found at https://github.com/aesptux/download-reddit-saved-images.

# Requirements

Outside standard library, redditcurl requires:
* `requests`
* `praw`
* `beautifulsoup4`

All of these can be downloaded with `pip`.

# Usage

To be able to access your saved images, redditcurl requires your username and password. You also need to tell it where the images should be saved.

    # redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images

By default, redditcurl will use 5 processes to process the links and download the images.
If you want to disable multiprocessing, or use more processes, you can pick the number of processes with `-c` or `--processes`.

Also by default, redditcurl will give names to the downloaded images, based on the titles of the reddit submissions. If you want to simply keep the names of the downloaded files, you can use `-n` or `--notitles`.

So for example, if you want redditcurl to download your saved images, and store them at `/home/karmanaut/images` without using their titles, and use 10 processes while downloading, you can do:

    # redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images -c 10 -n

If you want redditcurl to remove the images from your saved images as it downloads them, you can use `-r` or `--remove`.

Finally, redditcurl will print out some messages while it runs, including some warnings about failed downloads, and a total count of downloaded and failed images. If you don't want any output, you can use `-s` or `--silent`.

For example, if you want redditcurl to download the images, without using multiprocessing, print nothing while running, and remove the saved images if the downloads succeed, you can do:

    # redditcurl -u karmanaut -p hunter2 -d /home/karmanaut/images -c 1 -s -r

# Importing

redditcurl can be easily imported into your project.

    >>> import redditcurl
    >>> my_image = "http://i.imgur.com/gUQnp73.gif"
    >>> save_path = "/home/user/images"
    >>> redditcurl.manage_download(my_image, save_path)
    ('http://i.imgur.com/gUQnp73.gif', True)

`redditcurl.manage_download` will pick the correct function and download the image for you.
When download finishes, it will return a tuple, contaning the url and `True` if the download succeeded, `False` otherwise.

# Licensing

redditcurl is licensed with GPLv3. Please see the file `COPYING` for details.

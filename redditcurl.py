#!/usr/bin/env python3
"""
    redditcurl, download the images you saved on Reddit.
    Copyright (C) 2015  Kaan Genç

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import argparse
import os
import praw
import redditcurl


def __main__():
    try:
        parser = argparse.ArgumentParser(description="Downloads your saved images from Reddit.")
        parser.add_argument("-u", "--username", type=str, required=True,
                            help="Reddit username.")
        parser.add_argument("-p", "--password", type=str, required=True,
                            help="Reddit password.")
        parser.add_argument("-d", "--savedir", type=str, required=True,
                            help="Directory to save the images.")
        parser.add_argument("-c", "--processes", type=int, default=20,
                            help="Number of processes to use. "
                                 "Use 1 to disable multiprocessing.")
        parser.add_argument("-b", "--subfolders", action="store_true", default=False,
                            help="Put the images into subfolders, based on their subreddits.")
        parser.add_argument("-t", "--subreddits", type=str, default="",
                            help="Only download from specific subreddits. Seperate names with commas (,).")
        parser.add_argument("-n", "--notitles", action="store_true", default=False,
                            help="Do not use titles of submissions as file names, "
                                 "use the names of downloaded files instead.")
        parser.add_argument("-f", "--savefile", type=str, default=".downloaded.gz",
                            help="The file to keep track of images that have been downloaded.")
        parser.add_argument("-r", "--remove", action="store_true", default=False,
                            help="Remove the files that were successfully downloaded from saved.")
        parser.add_argument("-s", "--silent", action="store_true", default=False,
                            help="Do not print anything about the scripts actions.")
        args = parser.parse_args()
        if args.silent:
            prints = lambda x: None
        else:
            prints = print
        if args.subreddits == "":
            subreddits = []
        else:
            subreddits = args.subreddits.strip(',').casefold().split(',')
            print("Downloading from {}".format(subreddits))
        r = praw.Reddit(user_agent="Just {} downloading some images".format(args.username))
        prints("Logging in as {}.".format(args.username))
        r.login(username=args.username, password=args.password)
        prints("Logged in.")
        prints("Getting data...")
        try:
            os.makedirs(args.savedir)
        except (FileExistsError):
            pass
        save_file = os.path.join(args.savedir, args.savefile)
        saved = redditcurl.filter_new(r.user.get_saved(limit=None), save_file)
        prints("Starting to download, using {} processes.".format(args.processes))
        downloaded = redditcurl.download_submissions(saved, args.savedir, args.processes,
                                          not args.notitles, args.subfolders, subreddits)
        prints("Processed {} urls.".format(len(downloaded)))
        success_count = 0
        fail_count = 0
        successful_downloads = []
        for i, submission in enumerate(downloaded):
            url, successful = submission
            if not successful:
                fail_count += 1
                prints("Download failed: {}".format(url))
            else:  # successful
                success_count += 1
                successful_downloads.append(url)
                if args.remove:
                    saved[i].unsave()
        prints("Updating saved files list.")
        redditcurl.update_new(successful_downloads, save_file)
        prints("\nDownloading finished.")
        prints("Successful: {} \t Failed: {}".format(success_count, fail_count))
    except (praw.errors.InvalidUserPass):
        print("Wrong password!")

if __name__ == "__main__":
    __main__()

from setuptools import setup

setup(
    name="redditcurl",
    version="0.1",
    description="Download the images you saved on Reddit.",
    license="GPLv3",
    author="Kaan Genç",
    author_email="kaan_genc@outlook.com",
    url="https://github.com/SeriousBug/redditcurl",
    download_url="https://github.com/SeriousBug/redditcurl/tarball/0.1",
    install_requires=["praw", "requests", "beautifulsoup4"],
    keywords=["reddit", "images", "download"],
    packages=["redditcurl", "redditcurl/websites"],
    scripts=["redditcurl.py"],
    entry_points={
        "console_scripts": ["redditcurl = redditcurl:__main__"]
    }
)

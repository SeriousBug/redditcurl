from setuptools import setup

setup(
    name="redditcurl",
    version="0.1.1",
    description="Download the images you saved on Reddit.",
    license="GPLv3",
    author="Kaan Genç",
    author_email="kaan_genc@outlook.com",
    url="https://github.com/SeriousBug/redditcurl",
    download_url="https://github.com/SeriousBug/redditcurl/tarball/0.1.1",
    install_requires=["praw", "requests", "beautifulsoup4"],
    keywords=["reddit", "images", "download"],
    packages=["redditcurl", "redditcurl/websites"],
    scripts=["redditcurl_main.py"],
    entry_points={
        "console_scripts": ["redditcurl = redditcurl_main:__main__"]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ]
)

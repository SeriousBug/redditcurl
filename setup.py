from setuptools import setup


REPOSITORY = "https://github.com/SeriousBug/redditcurl"
VERSION = "0.3.0"


setup(
    name="redditcurl",
    version=VERSION,
    description="Download the images you saved on Reddit.",
    license="GPLv3",
    author="Kaan Genç",
    author_email="kaan_genc@outlook.com",
    url=REPOSITORY,
    download_url='/'.join((REPOSITORY, VERSION)),
    install_requires=["praw", "requests", "beautifulsoup4"],
    keywords=["reddit", "images", "download"],
    packages=["redditcurl", "redditcurl/websites"],
    entry_points={
        "console_scripts": ["redditcurl = redditcurl.__main__:__main__"],
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

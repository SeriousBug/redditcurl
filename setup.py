from setuptools import setup


setup(
    name="redditcurl",
    version="1.0.1",
    description="Download the images you saved on Reddit.",
    license="GPLv3",
    author="Kaan Genç",
    author_email="pypi@kaangenc.me",
    url="https://github.com/SeriousBug/redditcurl",
    download_url="https://github.com/SeriousBug/redditcurl/releases",
    install_requires=["praw", "requests", "beautifulsoup4"],
    keywords=["reddit", "images", "download"],
    packages=["redditcurl", "redditcurl/websites"],
    entry_points={
        "console_scripts": ["redditcurl = redditcurl.__main__:__main__"],
    },
    test_suite="tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ]
)

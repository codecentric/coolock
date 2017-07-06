import os
from setuptools import setup

setup(
    name = "coolock",
    version = "0.0.1",
    author = "Daniel Marks",
    author_email = "daniel.marks@codecentric.de",
    description = ("A coordinated locking wrapper script for distributed tasks"),
    license = "GPLv3",
    keywords = "coordination lock cron distributed",
    url = "http://packages.python.org/coolock",
    packages=['coolock'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
          'configargparse >= 0.10.0',
          'tooz >= 1.56.1',
      ],
    scripts=['scripts/coolock'],
)

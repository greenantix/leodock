#!/usr/bin/env python3

import sys

if sys.version_info < (3, 6, 0):
    print("Python 3.6+ is required")
    exit(1)
import io  # noqa E402
import os  # noqa E402
from setuptools import find_packages, setup  # noqa E402
from pathlib import Path  # noqa E402
from typing import List  # noqa E402
import ast  # noqa E402
import re  # noqa E402
import distutils.text_file

CURDIR = Path(__file__).parent

EXCLUDE_FROM_PACKAGES = ["tests*"]


with io.open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()




setup(
    name="leodock",
    version="1.0.0",
    author="greenantix",
    author_email="your-email@example.com",
    description="AI-powered development platform with integrated terminal and LLM collaboration",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/greenantix/leodock",
    license="License :: OSI Approved :: MIT License",
    packages=find_packages("src", exclude=EXCLUDE_FROM_PACKAGES),
    package_dir={"": "src"},
    include_package_data=True,
    keywords=[
        "ai",
        "llm",
        "development",
        "terminal",
        "browser",
        "collaboration",
        "python",
        "flask",
        "socketio",
    ],
    scripts=[],
    entry_points={"console_scripts": ["leodock = run_leodock:main"]},
    extras_require={},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=distutils.text_file.TextFile(
        filename="./requirements.txt"
    ).readlines(),
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
)

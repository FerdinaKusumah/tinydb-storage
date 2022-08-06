import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# read requirements from text
with open("requirements.txt") as f:
    required = f.read().splitlines()

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="tinydb-storage",
    version="0.1.0",
    description="Wrapper tinydb storage",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://mnc-repo.mncdigital.com/ai-team/vision_plus/rce_offline_results_module",
    author="Ferdina Kusumah",
    author_email="ferdina.kusumah@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[o for o in required if "#" not in o],
)

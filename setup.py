import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eoiv-sorter", # Replace with your own username
    version="0.0.2",
    author="Calvin Stewart",
    author_email="calvinxstewart@gmail.com",
    description="Example package in repo for testing integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calvinrs/test-rweoiv.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
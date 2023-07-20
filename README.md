# ffscrape

## Installation

For simplicity sake, I'm going to only support Debian based distros.

### Git clone this repo

``` bash

$ apt install git -y

$ cd ~

$ git clone https://github.com/Oddly/ffscrape.git
```

Code will now be inside a newly created ffscrape directory.

### Create and initialize a virtual environment

``` bash

$ python3 -m venv ~/virtualenv

$ source ~/virtualenv/bin/activate
```

You are now in a isolated environment, wherein modules you install with pip for Python are kept. When you leave this environment, these modules won't be available to you.

### Install the script requirements

Then, install the requirements for the script to work. Replace the directory with the place you did your git clone.

``` bash
$ cd ~/ffscrape

$ pip install -r ./requirements.txt
```

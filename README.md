# irasutoya-images-english

Translates june29's JSON format by adding a few elements and download the images.
Example:

```
    {
        "title": "聖火のイラスト",
        "description": "オリンピックなどの神聖な儀式で使うための火（松明）、聖火のイラストです。",
        "categories": [
            "スポーツ用具",
            "お祭り",
            "オリンピック",
            "道具"
        ],
        "entry_url": "http://www.irasutoya.com/2016/10/blog-post_365.html",
        "image_url": "https://3.bp.blogspot.com/-1b4TG3HQy4I/V9vCss23vQI/AAAAAAAA9_o/UVY7FalJ2lYxmTIV3CgkDY4C8LKBvpklQCLcB/s400/taimatsu_olympic.png",
        "image_alt": "聖火のイラスト",
        "published_at": "2016-10-16 09:00:00 +0000",
        "title_en": "Illustration of a torch",
        "description_en": "This is an illustration of a torch, a fire for use in sacred ceremonies such as the Olympics.",
        "categories_en": [
            "Sports equipment",
            "Festival",
            "Olympic",
            "Prop"
        ],
        "image_alt_en": "Illustration of a torch",
        "directory_path": "./images/2016/10/taimatsu_olympic.png"
    }
```

# Setup

## Download and install Python 3.7 from official website

[Download Python](https://www.python.org/downloads/)

## Install pipenv

```bash
pip install pipenv
```

## Install prerequisite packages

```bash
pipenv install
```

## Usage

```bash
Usage: iie.py [OPTIONS]

  Main function

Options:
  -d, --download   Download images
  -t, --translate  Create and translate original json to english
  --help           Show this message and exit.
  -r, --retries    Max retries if a problem occurs (network or API)

```

```bash
python iie.py
```

By default without any argument passed, the script will translate to English and download image files into local machine.

If you only want to download the images or just translate to English, use the argument:

```bash
python iie.py -d
```

or 

```bash
python iie.py -t
```

When you launch the script with the an existing `irasutoya_with_en.json` (left for convenience, since it takes a week to translate), it will start from where it was last stopped so it will only download the latest images and translate the latest descriptions.

Pull requests to improve this behavior and add options are welcome. :)


## Legal

The images are not included in this repository for copyright reasons.
Please note that if you use downloaded images in your project, you should take note of the author's terms: https://www.irasutoya.com/p/terms.html

## Credit

The original implementation of this script was done by [lazidoca](https://github.com/lazidoca?tab=repositories).
Now I am the one maintaining it.

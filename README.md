# Moly.hu Metadata source

Based on Hokutya's [moly.hu calibre plugin](https://www.mobileread.com/forums/showthread.php?t=193302) from mobileread.com.

Metadata from https://moly.hu

Supported applications:
- [calibre](https://calibre-ebook.com/)
- [calibre-web](https://github.com/janeczku/calibre-web)


Source code: https://github.com/crash5/calibre-molyhu

## Usage

Search for book in command-line: `python -m moly_hu.main "raymond feist"`

Include it in calibre-web docker yaml:
```
volumes:
  - moly_hu.py:/app/calibre-web/cps/metadata_provider/moly_hu.py:ro
  - moly_hu_provider.py:/app/calibre-web/cps/metadata_provider/moly_hu_provider.py:ro
```


## Contributing

- Plugin class
    - `calibre/src/calibre/customize/__init__.py`
    - https://manual.calibre-ebook.com/plugins.html#plugin
- (Metadata) Source class
    - `calibre/src/calibre/ebooks/metadata/sources/base.py`
    - https://manual.calibre-ebook.com/plugins.html#module-calibre.ebooks.metadata.sources.base
- (Book) Metadata class
    - `calibre/src/calibre/ebooks/metadata/book/base.py`
    - https://manual.calibre-ebook.com/_modules/calibre/ebooks/metadata/book/base.html


```
python -m venv .venv
source .venv/bin/activate
pip install -e moly_hu[dev]

python -m pytest -v moly_hu/tests/
```

Reload in calibre: `calibre-debug -s; calibre-customize -b .; calibre`

VSCode code completion (calibre and calibre-web is one level up in directory tree):
```
{
    "python.autoComplete.extraPaths": [
        "../calibre/src",
        "../calibre-web"
    ],
    "python.analysis.extraPaths": [
        "../calibre/src",
        "../calibre-web"
    ],
}
```

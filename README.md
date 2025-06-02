# Mega Zap ⚡️

Basic [Streamlit](https://streamlit.io) app to process records for published maps created via Zap ⚡️.

## Usage

https://mega-zap.streamlit.app (temporary hosting)

## Record requirements

- x3 product records following MAGIC profile (Overall Map, Side A, Side B)
- thumbnails set in all records (covers in Overall Map record, overviews in Side A/B record)

## Processing steps

- adds 'paper map product' local hierarchy level code list value to overall record (always)
- adds ISBN identifiers to records (if set)
- adds map series sheet number to records via supplemental info key-value (if set)
- adds MAGIC as an author if missing (always)
- sets the order of contacts inc. authors (always but changing order is optional)
- adds aggregations (relationships) between records: (always)
  - {Overall Map}:
    - 'this item is composed of {Side A} and {Side B} as a paper map'
  - {Side A}:
    - 'this item is part of the larger paper map {Overall Map}'
    - 'this item is the physical reverse of {Side A} as a paper map'
  - {Side B}:
    - 'this item is part of the larger paper map {Overall Map}'
    - 'this item is the physical reverse of {Side B} as a paper map'
- adds distribution option for purchasing physical maps to {Overall Map} (always)

## Limitations

- only two sided maps are supported (not single or atlases)
- only one map on each side is supported
- output records will give validation warnings for pending local code list values ('paperMapProduct', 'paperMap')
- doubt overall bbox is being calculated correctly
- no tests

## Notes

- Shouldn't include paper info in sides A/B?
  - i.e. do we tie A/B to a specific paper map and inherit info/context from it, or not? 
  - currently inconsistent but leaning towards tieing

## Development

Run locally:

```
% uv run -- streamlit run main.py
```

## Licence

Copyright (c) 2025 UK Research and Innovation (UKRI), British Antarctic Survey (BAS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

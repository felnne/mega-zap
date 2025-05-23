# Mega Zap ⚡️

Basic [Streamlit](https://streamlit.io) app to process records for published maps created via Zap ⚡️.

## Usage

```
% uv run -- streamlit run main.py
```

## Record requirements

- x3 product records following MAGIC profile (Overall Map, Side A, Side B)
- thumbnails set in all records (covers in Overall Map record, overviews in Side A/B record)

## Processing steps

- adds ISBN identifiers to records (if set)
- adds MAGIC as an author (always)
- copies thumbnails across records (always):
  - {Overall Map}:
    - overview: {Overall Map}
    - side_a: {Side A}
    - side_b: {Side B}
  - {Side A}:
    - overview: {Side A}
    - covers {Overall Map}
  - {Side B}:
    - overview: {Side B}
    - covers {Overall Map}
- adds aggregations (relationships) between records:
  - {Overall Map}:
    - 'this item is composed of {Side A} and {Side B} as a paper map'
  - {Side A}:
    - 'this item is part of the larger paper map {Overall Map}'
    - 'this item is the physical reverse of {Side A} as a paper map'
  - {Side B}:
    - 'this item is part of the larger paper map {Overall Map}'
    - 'this item is the physical reverse of {Side B} as a paper map'
- copies extents across records:
  - {Overall Map}:
    - bounding: union({Side A}, {Side B})
    - side_a: {Side A}
    - side_b: {Side B}
- adds distribution option for purchasing physical maps to {Overall Map}

## Limitations

- single sided maps not supported
- more than 1 map frame on a side not supported
- output records will give validation warnings for pending local code list value ('paperMap')
- thumbnail types not fully right yet
- doubt overall bbox is being calculated correctly
- we don't have anything that states 123 is side A and 234 is side B
- no tests

## Notes

- Shouldn't include paper info in sides A/B?
  - by that logic don't include ISBNs in sides A/B either?

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

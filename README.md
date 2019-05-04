## Installation

```
CFLAGS='-mmacosx-version-min=10.7 -stdlib=libc++' pip install plyvel --no-cache-dir --global-option=build_ext --global-option="-I/usr/local/Cellar/leveldb/1.20_2/include/" --global-option="-L/usr/local/lib"
```

if you see this error:

```python
import google.protobuf
```
and get the feedback
```bash
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    ImportError: No module named google.protobuf
```
Then do:
```bash
pip install --ignore-installed six
sudo pip install protobuf
```
should fix the issue.
```bash
Installing collected packages: protobuf
Successfully installed protobuf-3.7.1
```

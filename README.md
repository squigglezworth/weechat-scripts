# weechat scripts

### bufferlist.py

As awesome as the `buflist` plugin is, the format settings were getting far too complex to manage (one of my old buflist configs is still available [here](https://github.com/weechat/weechat/wiki/buflist#a-complex-example))  This is my attempt at writing my own script

Screenshot available [here](https://imgur.com/a/suab6pd)

#### Notes
- Assumes a left/right bar named `buffers` with vertical filling
- No mouse support. It will probably never be added

### read_marker,py

Somewhat hacky script that updates the `weechat.look.read_marker_string` setting so that a user-supplised string is always aligned to the sides - refreshes on window resize, results in drawing issues sometimes

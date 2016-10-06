# Discurses
A CLI for discord, written in python. The name is a combination of discord and curses, as in the terminal interface library. Discurses doesn't use curses, but i originally planned to. It is now built using urwid, a widget library which _can_ use curses as a rendering engine, but discurses works fine without it.

Questions, bug reports, PR's and comments are all very welcome.  

I can be contacted at `topisani@hamsterpoison.com`
![Discurses chat view](https://github.com/topisani/Discurses/raw/master/docs/graphics/img-2016-10-06-142806.png)

## Installation
### Linux
That one is pretty easy:

```shell
$ pip install discurses
```
Python 3.5 is required.

### Windows
Start out by following [https://wiki.archlinux.org/index.php/Installation_guide](this) guide.

After that, follow the instructions for linux above

## Authentication
Put the file `example_discurses.yaml` in your `~/.config/` directory, replace the placeholder with your discord token and rename the file to `discurses.yaml`.
You can get the token by visiting [https://discordapp.com/channels/@me](https://discordapp.com/channels/@me), opening the javascript console, and executing the command `localStorage.getItem("token")`.

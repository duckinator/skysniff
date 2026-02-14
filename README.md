# skysniff

Skysniff pulls weather information from the National Weather Service, and prints it to your terminal.

Basic usage: `skysniff [-a] daily` or `skysniff [-a] hourly`

You can store the [a default address in a config file](#storing-your-address), or pass `-a` to have it ask for an address.

## Installation

```
$ pipx install skysniff
```

## Usage

```console
$ cat ~/.config/skysniff/address.txt
Montello & Centre St, 02302
$ skysniff hourly
12AM 21°F, Mostly Cloudy, winds 5 mph
[...]
11AM 33°F, Mostly Sunny, winds 8 mph

$ skysniff daily -a
Address: Penn Ave & Negley Ave, Pittsburgh, PA
Overnight
---------
Mostly cloudy. Low around 26, with temperatures rising to around 32 overnight. Southwest wind around 6 mph.

[...]
```

### Storing your address

By default, skysniff will try to read your address from the address configuration file.

If the environment variable `$XDG_CONFIG_HOME` is defined, skysniff uses `$XDG_CONFIG_HOME/skysniff/address.txt`. Otherwise, it uses `~/.config/skysniff/address.txt`.

(Usually these are equivalent.)

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/skysniff. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The code for skysniff is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

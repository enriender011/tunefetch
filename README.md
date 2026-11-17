# tunefetch

English | [Español](README.es.md)

Command-line tool that searches music on several sources, picks the match with the best audio quality, and downloads
it. It uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) as its download engine and needs
[ffmpeg](https://ffmpeg.org) on your PATH.

## Install

Download the executable for your system from the
[releases page](https://github.com/enriender011/tunefetch/releases). ffmpeg must be on your PATH. If it is missing,
`tunefetch get` stops and shows how to install it (on Windows: `winget install Gyan.FFmpeg`, then open a new terminal).

On Windows nothing needs installing: put `tunefetch.exe` in any folder, open PowerShell there and run
`.\tunefetch.exe get "artist - title"`. The downloads are saved next to the `.exe`. The first time, Windows
SmartScreen may warn because the file is not signed: choose More info, then Run anyway. Each start takes a second or
two because the single file unpacks itself.

Or install from source:

```powershell
uv tool install git+https://github.com/enriender011/tunefetch
```

## Usage

```powershell
tunefetch get "artist - title"               # show the matches and choose which to download
tunefetch get "artist - title" --auto        # skip the menu and download the best match
tunefetch get "artist - title" -f m4a        # save as m4a (works on iPhone)
tunefetch get "artist - title" -o D:\Music   # save in another folder, only for this run
tunefetch get https://soundcloud.com/artist/sets/album   # an album or playlist: its songs go in a folder
tunefetch search "artist - title"            # list the matches without downloading
tunefetch search "artist - title" --quality  # also check the audio quality (slower)
tunefetch sources                            # show where it can search
```

`get` first identifies the track on [MusicBrainz](https://musicbrainz.org) to learn its exact artist, title and
duration. It then searches every source and checks the audio format of each match. Results are listed from best to
worst quality among the matches that fit the query as well as the best one does: lossless first, then the highest
bitrate (Opus and AAC count for more than MP3 at the same bitrate). A remix, a different song, a 30-second preview
or a version with a very different duration never ranks above the real track.

In a terminal it asks which to download: type a number, several numbers (`1,3`), Enter for the first, or `q` to
cancel. A progress bar shows the download. With `--auto`, or when the output is not a terminal, it downloads the best
match without asking. A URL is always downloaded directly.

## Where the files go

By default files are saved in the folder where `tunefetch.exe` is, wherever you run it from. When it runs from source
(`uv run` or `uv tool install`) there is no `.exe`, so it uses the folder you ran the command in. If that folder
cannot be written to (for example `C:\Program Files`), it uses your home folder instead. To choose another folder:

- `-o <folder>` changes it for one run.
- `tunefetch config output <folder>` changes it for good. `tunefetch config output auto` goes back to the default.

A single song is saved as a file. A link to an album or playlist with several songs creates a folder named after it,
and the songs go inside, numbered in order (`01 - Artist - Title.mp3`). A playlist with only one song does not
create a folder.

## Help and settings

`tunefetch --help` shows every command and option with examples, and `tunefetch <command> --help` shows one command
in detail.

There are two settings, shown and changed with `tunefetch config`:

```powershell
tunefetch config                      # show both settings and where the settings file is
tunefetch config output D:\Music      # download folder
tunefetch config output auto          # back to the default folder
tunefetch config language es          # always Spanish
tunefetch config language en          # always English
tunefetch config language auto        # follow the system language again
tunefetch --lang es get "..."         # change the language only for this run
```

The language (English or Spanish) follows your system by default. Its order of priority is `--lang`, then the
`TUNEFETCH_LANG` variable, then the saved setting, then the system. The download folder is chosen with `-o`, then the
saved setting, then the default folder described above. The settings file is `%APPDATA%\tunefetch\config.json` on Windows and
`~/.config/tunefetch/config.json` elsewhere.

## Output format

The default is `mp3` (VBR 0, about 245 kbps), which plays on every device. `-f m4a` (AAC 256 kbps) is the other
choice that works on iPhone and gives smaller files. `-f flac`, `opus` and `wav` also work. `-f best` keeps the
original audio without converting it. From YouTube that is a `.webm` file with Opus, which many players and iPhones
cannot open. Converting from a lossy source cannot restore quality, so the high conversion bitrates only avoid adding
more loss.

Files from an identified track are named `Artist - Title` and tagged with that artist and title. The identification
only counts when it clearly fits what you typed, so writing `artist - title` works best. If MusicBrainz is
unreachable or has no confident match, tunefetch continues without it. Use `--no-lookup` to skip it.

## About quality

Converting to FLAC does not add quality that the source never had. A track taken from YouTube is lossy
(usually Opus or AAC) even if you save it as FLAC. Real lossless audio only comes from sources that offer it.

## Sources

| Source     | Search by name | By URL |
| ---------- | -------------- | ------ |
| YouTube    | yes            | yes    |
| SoundCloud | yes            | yes    |
| Others supported by yt-dlp | no | may work, not tested |

Bandcamp links currently fail: Bandcamp blocks yt-dlp with an anti-bot check (checked in November 2026 with three albums), and tunefetch cannot work around it. Albums and playlists have been tested with YouTube and SoundCloud.

## Responsible use

Download only what you have the right to download: your own music, free-licensed or public-domain works, and
content that the service allows you to save. You are responsible for following the terms of each service and your
local law.

## Development

```powershell
uv sync
uv run pytest
uv run tunefetch --help
```

Every user-facing text lives in `src/tunefetch/i18n.py` in both languages, and a test fails if one language is
missing a message. Keep `README.md` and `README.es.md` in sync when you change either.

## Publishing a release

1. Change `__version__` in `src/tunefetch/__init__.py` and `version` in `pyproject.toml` (for example to `1.0.1`).
2. Write the release notes in `docs/releases/v1.0.1.md`, in English and Spanish like the other files there.
3. Commit and push, then create and push the tag: `git tag v1.0.1` and `git push origin v1.0.1`.
4. Watch the Release workflow in the Actions tab of the repository. It runs the tests, builds `tunefetch.exe` for
   Windows, checks that it starts, writes `SHA256SUMS.txt` and creates a **draft** release with the notes.
5. On GitHub, open Releases, edit the draft, read it, and press Publish release. Nothing is public until then.

If the workflow fails, fix the problem, delete the tag (`git tag -d v1.0.1`, `git push origin :refs/tags/v1.0.1`) and
create it again.

## License

MIT

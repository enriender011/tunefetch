# tunefetch

Command-line tool that searches music on several sources, picks the match with the best audio quality, and downloads
it. It uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) as its download engine and needs
[ffmpeg](https://ffmpeg.org) on your PATH.

## Install

```powershell
uv tool install .
```

## Usage

```powershell
tunefetch search "artist - title"            # list matches
tunefetch search "artist - title" --quality  # also check the audio quality (slower)
tunefetch get "artist - title"               # pick the best match and download it
tunefetch get "artist - title" -f mp3        # convert to mp3
tunefetch get https://artist.bandcamp.com/album/name -o music
tunefetch sources
```

`get` searches every source, keeps the matches that fit your query, checks the audio format each one offers, and
downloads the best. Lossless formats rank first, then the highest bitrate. By default it keeps the original audio
without re-encoding.

## About quality

Converting to FLAC does not add quality that the source never had. A track taken from YouTube is lossy
(usually Opus or AAC) even if you save it as FLAC. Real lossless audio only comes from sources that offer it.

## Sources

| Source     | Search by name | By URL |
| ---------- | -------------- | ------ |
| YouTube    | yes            | yes    |
| SoundCloud | yes            | yes    |
| Others supported by yt-dlp (Bandcamp, Internet Archive...) | no | yes |

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

## License

MIT

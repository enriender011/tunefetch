# tunefetch

[English](README.md) | Español

Herramienta de línea de comandos que busca música en varias fuentes, elige la coincidencia con mejor calidad de audio
y la descarga. Usa [yt-dlp](https://github.com/yt-dlp/yt-dlp) como motor de descarga y necesita
[ffmpeg](https://ffmpeg.org) en el PATH.

## Instalación

Descarga el ejecutable para tu sistema desde la
[página de releases](https://github.com/enriender011/tunefetch/releases). ffmpeg debe estar en el PATH. Si falta,
`tunefetch get` se detiene y muestra cómo instalarlo (en Windows: `winget install Gyan.FFmpeg`, y abre un terminal
nuevo).

En Windows no hace falta instalar nada: pon `tunefetch.exe` en cualquier carpeta, abre PowerShell ahí y ejecuta
`.\tunefetch.exe get "artista - título"`. Las descargas se guardan junto al `.exe`. La primera vez, Windows
SmartScreen puede avisar porque el archivo no está firmado: elige Más información y después Ejecutar de todas formas.
Cada arranque tarda uno o dos segundos porque el archivo único se descomprime solo.

O instálalo desde el código fuente:

```powershell
uv tool install git+https://github.com/enriender011/tunefetch
```

## Uso

```powershell
tunefetch get "artista - título"               # muestra las coincidencias y eliges cuál descargar
tunefetch get "artista - título" --auto        # sin menú: descarga la mejor coincidencia
tunefetch get "artista - título" -f m4a        # guarda en m4a (funciona en iPhone)
tunefetch get "artista - título" -o D:\Music   # guarda en otra carpeta, solo en esta ejecución
tunefetch get https://soundcloud.com/artista/sets/album   # un álbum o lista: sus canciones van a una carpeta
tunefetch search "artista - título"            # lista las coincidencias sin descargar
tunefetch search "artista - título" --quality  # comprueba también la calidad de audio (más lento)
tunefetch sources                              # muestra dónde puede buscar
```

`get` primero identifica la canción en [MusicBrainz](https://musicbrainz.org) para saber su artista, título y
duración exactos. Después busca en todas las fuentes y comprueba el formato de audio de cada coincidencia. Los
resultados se ordenan de mejor a peor calidad entre las coincidencias que encajan con tu búsqueda tan bien como la
mejor: primero sin pérdida, luego el mayor bitrate (Opus y AAC valen más que MP3 al mismo bitrate). Un remix, otra
canción, una vista previa de 30 segundos o una versión con una duración muy distinta nunca quedan por encima de la
canción real.

En un terminal pregunta qué descargar: escribe un número, varios números (`1,3`), Enter para el primero o `q` para
cancelar. Una barra de progreso muestra la descarga. Con `--auto`, o cuando la salida no es un terminal, descarga la
mejor coincidencia sin preguntar. Un enlace siempre se descarga directamente.

## Dónde van los archivos

Por defecto los archivos se guardan en la carpeta donde está `tunefetch.exe`, ejecutes donde ejecutes. Si se usa desde el
código fuente (`uv run` o `uv tool install`) no hay `.exe`, así que usa la carpeta desde donde lanzaste el comando. Si
en esa carpeta no se puede escribir (por ejemplo `C:\Program Files`), usa tu carpeta personal. Para elegir otra:

- `-o <carpeta>` la cambia solo en esa ejecución.
- `tunefetch config output <carpeta>` la cambia para siempre. `tunefetch config output auto` vuelve a la
  predeterminada.

Una sola canción se guarda como archivo. Un enlace a un álbum o lista con varias canciones crea una carpeta con su
nombre, y las canciones van dentro, numeradas en orden (`01 - Artista - Título.mp3`). Una lista con una sola canción no
crea carpeta.

## Ayuda y ajustes

`tunefetch --help` muestra todos los comandos y opciones con ejemplos, y `tunefetch <comando> --help` muestra un
comando en detalle.

Hay dos ajustes, que se ven y se cambian con `tunefetch config`:

```powershell
tunefetch config                      # muestra los dos ajustes y dónde está el archivo de ajustes
tunefetch config output D:\Music      # carpeta de descargas
tunefetch config output auto          # vuelve a la carpeta predeterminada
tunefetch config language es          # siempre en español
tunefetch config language en          # siempre en inglés
tunefetch config language auto        # vuelve a seguir al idioma del sistema
tunefetch --lang en get "..."         # cambia el idioma solo en esta ejecución
```

El idioma (inglés o español) sigue al de tu sistema por defecto. Su orden de prioridad es `--lang`, luego la variable
`TUNEFETCH_LANG`, luego el ajuste guardado y por último el sistema. La carpeta de descargas se elige con `-o`, luego el
ajuste guardado y por último la carpeta predeterminada descrita arriba. El archivo de ajustes es `%APPDATA%\tunefetch\config.json` en
Windows y `~/.config/tunefetch/config.json` en el resto.

## Formato de salida

Por defecto es `mp3` (VBR 0, unos 245 kbps), que suena en cualquier dispositivo. `-f m4a` (AAC 256 kbps) es la otra
opción que funciona en iPhone y da archivos más pequeños. También valen `-f flac`, `opus` y `wav`. `-f best` conserva
el audio original sin convertirlo. Desde YouTube eso es un archivo `.webm` con Opus, que muchos reproductores y los
iPhone no pueden abrir. Convertir desde una fuente con pérdida no recupera calidad, así que los bitrates altos de
conversión solo evitan perder más.

Los archivos de una canción identificada se llaman `Artista - Título` y llevan ese artista y título en las etiquetas.
La identificación solo cuenta cuando encaja claramente con lo que escribiste, así que funciona mejor si escribes
`artista - título`. Si MusicBrainz no responde o no hay una coincidencia fiable, tunefetch sigue sin ella. Usa
`--no-lookup` para saltártela.

## Sobre la calidad

Convertir a FLAC no añade calidad que la fuente nunca tuvo. Una pista de YouTube tiene pérdida (normalmente Opus o
AAC) aunque la guardes como FLAC. El audio sin pérdida real solo viene de fuentes que lo ofrecen.

## Fuentes

| Fuente     | Búsqueda por nombre | Por enlace |
| ---------- | ------------------- | ---------- |
| YouTube    | sí                  | sí         |
| SoundCloud | sí                  | sí         |
| Otras compatibles con yt-dlp | no | pueden funcionar, sin probar |

Los enlaces de Bandcamp fallan ahora mismo: Bandcamp bloquea a yt-dlp con una comprobación anti-bot (comprobado en noviembre de 2026 con tres álbumes) y tunefetch no puede evitarlo. Los álbumes y listas se han probado con YouTube y SoundCloud.

## Uso responsable

Descarga solo lo que tengas derecho a descargar: tu propia música, obras con licencia libre o de dominio público, y
contenido que el servicio te permita guardar. Eres responsable de cumplir las condiciones de cada servicio y la ley de
tu país.

## Desarrollo

```powershell
uv sync
uv run pytest
uv run tunefetch --help
```

Todos los textos que ve el usuario están en `src/tunefetch/i18n.py` en los dos idiomas, y un test falla si a un idioma
le falta algún mensaje. Mantén `README.md` y `README.es.md` sincronizados cuando cambies uno de los dos.

## Publicar un release

1. Cambia `__version__` en `src/tunefetch/__init__.py` y `version` en `pyproject.toml` (por ejemplo a `1.0.1`).
2. Escribe las notas de la release en `docs/releases/v1.0.1.md`, en inglés y español como los demás archivos de ahí.
3. Haz commit y push, y después crea la etiqueta y súbela: `git tag v1.0.1` y `git push origin v1.0.1`.
4. Mira el workflow de Release en la pestaña Actions del repositorio. Pasa los tests, compila `tunefetch.exe` para
   Windows, comprueba que arranca, escribe `SHA256SUMS.txt` y crea una release en **borrador** con las notas.
5. En GitHub, abre Releases, edita el borrador, léelo y pulsa Publish release. Hasta entonces no es público.

Si el workflow falla, arregla el problema, borra la etiqueta (`git tag -d v1.0.1`, `git push origin :refs/tags/v1.0.1`)
y créala de nuevo.

## Licencia

MIT

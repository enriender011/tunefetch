from __future__ import annotations

LANGUAGES = {"en": "English", "es": "Español"}
DEFAULT_LANGUAGE = "en"

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        # help layout
        "help.tagline": "Search music on several sources and download the best available quality.",
        "help.usage": "Usage",
        "help.commands": "Commands",
        "help.examples": "Examples",
        "help.options": "Options",
        "help.arguments": "Arguments",
        "help.general": "General options",
        "help.environment": "Environment variables",
        "env.lang": "Language (en or es). The --lang option takes priority",
        "env.config_dir": "Folder of the settings file (default: %APPDATA%\\tunefetch on Windows)",
        "help.get_options": "Options of get",
        "help.search_options": "Options of search",
        "help.settings": "Settings",
        "help.footer": "Run `tunefetch <command> --help` to see every option of a command.",
        "ph.song": "song",
        "ph.link": "link",
        "ph.folder": "folder",
        "ph.format": "format",
        "ph.name": "name",
        "ph.number": "number",
        "ph.setting": "setting",
        "ph.value": "value",
        "usage.main": "tunefetch <command> [options]",
        "usage.get": "tunefetch get <song|link> [options]",
        "usage.search": "tunefetch search <song> [options]",
        "usage.sources": "tunefetch sources",
        "usage.config": "tunefetch config [setting] [value]",
        # command summaries (main help)
        "cmd.get": "Search a song and download it, or download a link",
        "cmd.search": "Only search: list the matches without downloading",
        "cmd.sources": "Show where tunefetch can search",
        "cmd.config": "Show or change settings (language, download folder)",
        # command descriptions (command help)
        "desc.get": (
            "Finds the song on YouTube and SoundCloud, orders the results from best to worst quality and lets you "
            "choose which to download. With a link, it downloads it directly. A single song is saved as a file; an "
            "album or playlist with several songs is saved in its own folder named after it. Files go to the folder "
            "of the program unless you use -o or change it with `tunefetch config output`."
        ),
        "desc.search": "Lists the matches for a song without downloading anything.",
        "desc.sources": "Lists the sources where tunefetch can search by name.",
        "desc.config": (
            "Without arguments it shows the current settings. With a setting and a value it changes it. "
            "Use `auto` as the value to go back to the default."
        ),
        "set.language": "Language of the messages: en, es or auto (follow the system)",
        "set.output": "Download folder: any path, or auto for the folder of the program",
        # arguments and options
        "arg.get.query": 'Song as "artist - title", or a link to a track, album or playlist',
        "arg.search.query": 'Song as "artist - title"',
        "arg.config.setting": "Setting to show or change (language, output)",
        "arg.config.value": "New value, or auto to go back to the default",
        "opt.output": "Folder where the files are saved, only for this run (default: the folder of the program, see `config`)",
        "opt.format": "mp3 (default), m4a (works on iPhone), flac, opus, wav, or best (original audio, usually .webm)",
        "opt.auto": "Skip the menu and download the best result",
        "opt.source": "Where to search: youtube, soundcloud (default: both)",
        "opt.limit": "Results per source (default: 3)",
        "opt.no_lookup": "Do not identify the song on MusicBrainz (it gives the exact name and duration)",
        "opt.quality": "Also check the audio quality of each result (slower)",
        "opt.lang": "Language for this run: en or es",
        "opt.version": "Show the version",
        "opt.help": "Show this help",
        # examples
        "ex.main.get": "Choose a result from a menu and download it",
        "ex.main.auto": "Download the best result without asking",
        "ex.main.m4a": "Save it as m4a (works on iPhone)",
        "ex.main.link": "Download a track, album or playlist from a link",
        "ex.main.output": "Save it in another folder",
        "ex.main.config_output": "Always download to that folder",
        "ex.main.lang": "Change the language",
        "ex.get.menu": "Choose from a menu",
        "ex.get.auto": "Download the best result without asking",
        "ex.get.format": "Convert to m4a",
        "ex.get.output": "Save in the folder D:\\Music",
        "ex.get.album": "Download an album: its songs go in a folder with the album name",
        "ex.search.basic": "List the matches",
        "ex.search.quality": "List them and check their audio quality",
        "ex.sources.list": "List the sources",
        "ex.config.show": "Show the settings",
        "ex.config.set": "Use Spanish",
        "ex.config.auto": "Pick the language from your system",
        "ex.config.output": "Always download to D:\\Music",
        "ex.config.output_auto": "Go back to the default folder",
        # run messages
        "run.identifying": "Identifying the track...",
        "run.identified": "Identified: {name}{length}",
        "run.not_identified": "Could not identify the track. Using the search text for names and matching.",
        "run.searching": "Searching...",
        "run.checking_quality": "Checking the audio quality...",
        "run.search_failed": "[{source}] search failed: {error}",
        "run.no_results": "No results.",
        "run.no_confident": "No confident match found. Run `tunefetch get` without --auto to choose from the candidates.",
        "run.downloading": "Downloading [{source}] {title} ({quality})",
        "run.downloading_link": "Downloading {url}",
        "run.failed": "Failed: {error}",
        "run.saved_in": "Saved in {path}",
        "run.cancelled": "Cancelled.",
        "run.error": "Error: {error}",
        "run.parse_error": "tunefetch: error: {message}\nRun `tunefetch --help` for help.",
        "err.unknown_command": "Unknown command '{value}'. Available: {options}.",
        "err.invalid_choice": "'{value}' is not valid for {arg}. Choose from: {options}.",
        "err.invalid_number": "{arg} needs a whole number, not '{value}'.",
        "err.needs_value": "{arg} needs a value.",
        "err.unrecognized": "Unknown option or extra argument: {value}. See `tunefetch --help`.",
        "run.ffmpeg_missing": (
            "Missing {tools}. tunefetch needs ffmpeg to convert the audio and write the tags.\n"
            "Install it and open a new terminal:\n"
            "  Windows: winget install Gyan.FFmpeg\n"
            "  macOS:   brew install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg"
        ),
        "run.missing_get": 'Missing the song or link. Example: tunefetch get "Estopa - Vino tinto"',
        "run.missing_search": 'Missing the song. Example: tunefetch search "Estopa - Vino tinto"',
        "menu.prompt": "Choose 1-{count} (several: 1,3), Enter = 1, q = cancel: ",
        "menu.invalid": "'{part}' is not a number between 1 and {count}.",
        "result.quality_unknown": "quality unknown",
        "result.lossless": "lossless",
        "result.match": "match {percent}",
        # sources and config
        "sources.more": "Any other site supported by yt-dlp may work if you pass its link to `get`. Bandcamp currently blocks yt-dlp, so its links fail.",
        "config.language": "Language: {name} ({code}), {origin}",
        "config.file": "Settings file: {path}",
        "config.set": "Language set to {name}.",
        "config.reset": "Language set to automatic.",
        "config.bad_language": "Unknown language '{value}'. Use one of: {options}.",
        "config.bad_setting": "Unknown setting '{setting}'. Available: {options}.",
        "config.output": "Download folder: {path}, {origin}",
        "config.output_set": "Download folder set to {path}.",
        "config.output_reset": "Download folder set to the default: {path}.",
        "config.output_is_file": "'{path}' is a file, not a folder.",
        "origin.flag": "from --lang",
        "origin.env": "from the TUNEFETCH_LANG variable",
        "origin.config": "from your settings",
        "origin.system": "from your system",
        "origin.default": "default",
    },
    "es": {
        # help layout
        "help.tagline": "Busca música en varias fuentes y descarga la mejor calidad disponible.",
        "help.usage": "Uso",
        "help.commands": "Comandos",
        "help.examples": "Ejemplos",
        "help.options": "Opciones",
        "help.arguments": "Argumentos",
        "help.general": "Opciones generales",
        "help.environment": "Variables de entorno",
        "env.lang": "Idioma (en o es). La opción --lang tiene prioridad",
        "env.config_dir": "Carpeta del archivo de ajustes (por defecto: %APPDATA%\\tunefetch en Windows)",
        "help.get_options": "Opciones de get",
        "help.search_options": "Opciones de search",
        "help.settings": "Ajustes",
        "help.footer": "Ejecuta `tunefetch <comando> --help` para ver todas las opciones de un comando.",
        "ph.song": "canción",
        "ph.link": "enlace",
        "ph.folder": "carpeta",
        "ph.format": "formato",
        "ph.name": "nombre",
        "ph.number": "número",
        "ph.setting": "ajuste",
        "ph.value": "valor",
        "usage.main": "tunefetch <comando> [opciones]",
        "usage.get": "tunefetch get <canción|enlace> [opciones]",
        "usage.search": "tunefetch search <canción> [opciones]",
        "usage.sources": "tunefetch sources",
        "usage.config": "tunefetch config [ajuste] [valor]",
        # command summaries (main help)
        "cmd.get": "Busca una canción y la descarga, o descarga un enlace",
        "cmd.search": "Solo busca: lista las coincidencias sin descargar",
        "cmd.sources": "Muestra dónde puede buscar tunefetch",
        "cmd.config": "Muestra o cambia los ajustes (idioma, carpeta de descargas)",
        # command descriptions (command help)
        "desc.get": (
            "Busca la canción en YouTube y SoundCloud, ordena los resultados de mejor a peor calidad y te deja "
            "elegir cuál descargar. Con un enlace, lo descarga directamente. Una sola canción se guarda como "
            "archivo; un álbum o lista con varias canciones se guarda en su propia carpeta con su nombre. Los "
            "archivos van a la carpeta del programa, salvo que uses -o o lo cambies con `tunefetch config output`."
        ),
        "desc.search": "Lista las coincidencias de una canción sin descargar nada.",
        "desc.sources": "Lista las fuentes donde tunefetch puede buscar por nombre.",
        "desc.config": (
            "Sin argumentos muestra los ajustes actuales. Con un ajuste y un valor lo cambia. "
            "Usa `auto` como valor para volver al predeterminado."
        ),
        "set.language": "Idioma de los mensajes: en, es o auto (sigue al sistema)",
        "set.output": "Carpeta de descargas: cualquier ruta, o auto para la carpeta del programa",
        # arguments and options
        "arg.get.query": 'Canción como "artista - título", o un enlace a una pista, álbum o lista',
        "arg.search.query": 'Canción como "artista - título"',
        "arg.config.setting": "Ajuste que quieres ver o cambiar (language, output)",
        "arg.config.value": "Valor nuevo, o auto para volver al predeterminado",
        "opt.output": "Carpeta donde se guardan los archivos, solo en esta ejecución (por defecto: la carpeta del programa, ver `config`)",
        "opt.format": "mp3 (por defecto), m4a (funciona en iPhone), flac, opus, wav, o best (audio original, normalmente .webm)",
        "opt.auto": "Sin menú: descarga el mejor resultado",
        "opt.source": "Dónde buscar: youtube, soundcloud (por defecto: las dos)",
        "opt.limit": "Resultados por fuente (por defecto: 3)",
        "opt.no_lookup": "No identificar la canción en MusicBrainz (da el nombre y la duración exactos)",
        "opt.quality": "Comprueba también la calidad de audio de cada resultado (más lento)",
        "opt.lang": "Idioma de esta ejecución: en o es",
        "opt.version": "Muestra la versión",
        "opt.help": "Muestra esta ayuda",
        # examples
        "ex.main.get": "Elige un resultado en un menú y lo descarga",
        "ex.main.auto": "Descarga el mejor resultado sin preguntar",
        "ex.main.m4a": "Lo guarda en m4a (funciona en iPhone)",
        "ex.main.link": "Descarga una pista, álbum o lista desde un enlace",
        "ex.main.output": "Lo guarda en otra carpeta",
        "ex.main.config_output": "Descarga siempre en esa carpeta",
        "ex.main.lang": "Cambia el idioma",
        "ex.get.menu": "Elegir en un menú",
        "ex.get.auto": "Descargar el mejor resultado sin preguntar",
        "ex.get.format": "Convertir a m4a",
        "ex.get.output": "Guardar en la carpeta D:\\Music",
        "ex.get.album": "Descargar un álbum: sus canciones van a una carpeta con el nombre del álbum",
        "ex.search.basic": "Listar las coincidencias",
        "ex.search.quality": "Listarlas y comprobar su calidad de audio",
        "ex.sources.list": "Listar las fuentes",
        "ex.config.show": "Ver los ajustes",
        "ex.config.set": "Usar español",
        "ex.config.auto": "Elegir el idioma según tu sistema",
        "ex.config.output": "Descargar siempre en D:\\Music",
        "ex.config.output_auto": "Volver a la carpeta predeterminada",
        # run messages
        "run.identifying": "Identificando la canción...",
        "run.identified": "Identificada: {name}{length}",
        "run.not_identified": "No se pudo identificar la canción. Se usa el texto de búsqueda para los nombres y la comparación.",
        "run.searching": "Buscando...",
        "run.checking_quality": "Comprobando la calidad del audio...",
        "run.search_failed": "[{source}] la búsqueda falló: {error}",
        "run.no_results": "Sin resultados.",
        "run.no_confident": "No hay ninguna coincidencia fiable. Ejecuta `tunefetch get` sin --auto para elegir entre los candidatos.",
        "run.downloading": "Descargando [{source}] {title} ({quality})",
        "run.downloading_link": "Descargando {url}",
        "run.failed": "Falló: {error}",
        "run.saved_in": "Guardado en {path}",
        "run.cancelled": "Cancelado.",
        "run.error": "Error: {error}",
        "run.parse_error": "tunefetch: error: {message}\nEjecuta `tunefetch --help` para ver la ayuda.",
        "err.unknown_command": "Comando desconocido '{value}'. Disponibles: {options}.",
        "err.invalid_choice": "'{value}' no es válido para {arg}. Elige entre: {options}.",
        "err.invalid_number": "{arg} necesita un número entero, no '{value}'.",
        "err.needs_value": "{arg} necesita un valor.",
        "err.unrecognized": "Opción desconocida o argumento sobrante: {value}. Mira `tunefetch --help`.",
        "run.ffmpeg_missing": (
            "Falta {tools}. tunefetch necesita ffmpeg para convertir el audio y escribir las etiquetas.\n"
            "Instálalo y abre un terminal nuevo:\n"
            "  Windows: winget install Gyan.FFmpeg\n"
            "  macOS:   brew install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg"
        ),
        "run.missing_get": 'Falta la canción o el enlace. Ejemplo: tunefetch get "Estopa - Vino tinto"',
        "run.missing_search": 'Falta la canción. Ejemplo: tunefetch search "Estopa - Vino tinto"',
        "menu.prompt": "Elige 1-{count} (varias: 1,3), Enter = 1, q = cancelar: ",
        "menu.invalid": "'{part}' no es un número entre 1 y {count}.",
        "result.quality_unknown": "calidad desconocida",
        "result.lossless": "sin pérdida",
        "result.match": "coincidencia {percent}",
        # sources and config
        "sources.more": "Cualquier otro sitio compatible con yt-dlp puede funcionar si le pasas su enlace a `get`. Bandcamp bloquea ahora mismo a yt-dlp, así que sus enlaces fallan.",
        "config.language": "Idioma: {name} ({code}), {origin}",
        "config.file": "Archivo de ajustes: {path}",
        "config.set": "Idioma cambiado a {name}.",
        "config.reset": "Idioma en automático.",
        "config.bad_language": "Idioma desconocido '{value}'. Usa uno de: {options}.",
        "config.bad_setting": "Ajuste desconocido '{setting}'. Disponibles: {options}.",
        "config.output": "Carpeta de descargas: {path}, {origin}",
        "config.output_set": "Carpeta de descargas cambiada a {path}.",
        "config.output_reset": "Carpeta de descargas en la predeterminada: {path}.",
        "config.output_is_file": "'{path}' es un archivo, no una carpeta.",
        "origin.flag": "por --lang",
        "origin.env": "por la variable TUNEFETCH_LANG",
        "origin.config": "de tus ajustes",
        "origin.system": "según tu sistema",
        "origin.default": "por defecto",
    },
}

_current = DEFAULT_LANGUAGE


def set_language(code: str) -> None:
    global _current
    _current = code if code in MESSAGES else DEFAULT_LANGUAGE


def get_language() -> str:
    return _current


def t(key: str, **values: object) -> str:
    text = MESSAGES[_current].get(key) or MESSAGES[DEFAULT_LANGUAGE][key]
    return text.format(**values) if values else text

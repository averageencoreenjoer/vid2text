"""File types the converter is willing to pick up from an input folder."""

VIDEO_EXTENSIONS = frozenset({
    ".mp4", ".m4v", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".f4v", ".webm",
    ".mpg", ".mpeg", ".mpe", ".m2v", ".ts", ".mts", ".m2ts", ".3gp", ".3g2",
    ".ogv", ".vob", ".asf", ".rm", ".rmvb", ".divx", ".mxf", ".dv",
})

# Plain audio works too, since the first step is always "extract the sound".
AUDIO_EXTENSIONS = frozenset({
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".oga", ".opus", ".wma", ".amr",
})

MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

OUTPUT_FORMATS = ("txt", "json")

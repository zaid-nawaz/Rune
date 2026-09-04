from app.video.operations.trim import trim_video
from app.video.operations.crop import crop_video
from app.video.operations.resize import resize_video
from app.video.operations.volume import change_volume
from app.video.operations.music import add_background_music
from app.video.operations.subtitles import add_subtitles


OPERATIONS = {
    "trim": trim_video,
    "crop": crop_video,
    "resize": resize_video,
    "volume": change_volume,
    "background_music": add_background_music,
    "subtitles": add_subtitles,
}

from glob import iglob
import re
import datetime
from subprocess import Popen, check_output
import hashlib
import send_email as emailer
import configparser
import os
import shutil
import uuid
import tempdir

config = configparser.ConfigParser()
config.read('daily_video.cfg')

frames_path = config.get('File Paths', 'frames_path')
project_root = config.get('File Paths', 'project_root')
video_path = config.get('File Paths', 'video_out_path')

duration = config.get('Video Settings', 'duration')

send_list = [x.strip() for x in config.get('Email Settings', 'send_list').split(',')]
message = config.get('Email Settings', 'message')

ffmpeg_command = "/usr/local/bin/ffmpeg -framerate {} -pattern_type glob -i '{}' -c:v libx264 -r 30 -pix_fmt yuv420p {}/{}/{}"

def get_glob():
    today = datetime.datetime.today()
    today_str = today.strftime("%Y%m%d")

    yesterday = today - datetime.timedelta(1)
    yesterday_str = yesterday.strftime("%Y%m%d")

    glob_str = "{" + "*{0}19*,*{0}2*,".format(yesterday_str) + \
               ",".join(["*{}{:02}*".format(today_str, i) for i in range(0, 10)]) + "}"

    return "{}/{}.jpg".format(frames_path, glob_str)


def add_timestamp(frames, temp_path):
    def get_time(file_name):
        timestamp = re.search("_(\\d{14})_", file_name).group(1)
        timestamp = datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        return timestamp.strftime("%I:%M %p")

    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    from tempfile import NamedTemporaryFile
    font = ImageFont.truetype("SanFranciscoDisplay-Regular.otf", 30)

    # Populate temporary folder
    for i, file_name in enumerate(check_output("ls " + frames, shell=True).strip().split('\n')):
        img = Image.open(file_name)
        draw = ImageDraw.Draw(img)
        draw.text((10, 440), get_time(file_name), (255,255,255), font=font)
        import ntpath

        img.save('{}/{}'.format(temp_path, ntpath.basename(file_name)))

    return "{}/*.jpg".format(temp_path)

def make_video(frames):
    m = hashlib.sha256()
    m.update(datetime.datetime.today().strftime("%Y%m%d"))
    video_name = m.hexdigest() + ".mp4"

    print(ffmpeg_command.format(duration,
                              frames,
                              project_root,
                              video_path,
                              video_name))

    process = Popen(ffmpeg_command.format(duration,
                                          frames,
                                          project_root,
                                          video_path,
                                          video_name),
                    shell=True)
    process.wait()

    return "{}/{}".format(video_path, video_name)


def send_email(video_url):
    for to in send_list:
        emailer.send_email(to=to,
                           subject="Video for {}".format(datetime.datetime.today().strftime("%m/%d/%Y")),
                           message=message.format("cb6111.myfoscam.org:5432",
                                                                                   video_url),
                           html=True)


with tempdir.TempDir() as t:
    make_video(add_timestamp(get_glob(), t))
    # send_email(make_video(add_timestamp(get_glob(), t)))

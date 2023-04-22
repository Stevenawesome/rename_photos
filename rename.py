import PIL.Image
import PIL.ExifTags
import datetime
import os
import pathlib
import re
from exif import Image

import sys
import hashlib
import logging.config
import logging
import datetime
import imghdr

logging.config.fileConfig('logger.config')
logger = logging.getLogger(__name__)


class Pic:
    def __init__(self, folder):
        self.count = 0
        self.folder = folder
        self.mapping = {}

    def get_exif_info(self, image, folder):
        tag_value = {}

        try:
            image_handle = PIL.Image.open(image)
            if not image_handle.getexif():
                logger.error(f'no meta data for {image} under {folder}, return original data')
                return False
            info = image_handle.getexif()
            for tag_id in info:
                tag = PIL.ExifTags.TAGS.get(tag_id, tag_id)
                value = info.get(tag_id)
                if isinstance(value, bytes):
                    try:
                        value = value.decode()
                    except Exception as e:
                        continue
                tag_value[tag] = value
                if 'Date' in tag or 'date' in tag:
                    print(image, tag, value)
                    print(tag_value, '\n\n')
                    logger.info(f'{tag} {value}')
            if 'DateTimeOriginal' not in tag_value and 'DateTimeDigitized' not in tag_value and 'DateTime' not in tag_value:
                logger.info('no meta date, using current file date')
                return False
            if 'DateTimeOriginal' in tag_value:
                original_timestamp = tag_value['DateTimeOriginal']
            elif 'DateTimeDigitized' in tag_value:
                original_timestamp = tag_value['DateTimeDigitized']
            else:  # if 'DateTime' in tag_value:
                original_timestamp = tag_value['DateTime']
                logger.debug(f"get date time for {image}, which is {tag_value['DateTime']}")
                # file_stat_path = pathlib.Path(image)
                # curtime = datetime.datetime.fromtimestamp(file_stat_path.stat().st_ctime)
                # original_timestamp = curtime.strftime("%Y%m%d_%H%M%S")
            original_timestamp = re.split(':|\t|\n|\s', original_timestamp)
            original_timestamp = ''.join(original_timestamp + ['_'] + [image]) + '.jpg'
            self.count += 1
            return original_timestamp
        except AttributeError as ate:
            logger.error(f'no attribute {ate} for {image} under {folder}')
            return None
        except Exception as e:
            logger.error(f'other error {e} for {image} under {folder}')
            return None

    def rename_photo(self, photo, folder):
        if not self.get_exif_info(photo, folder):
            return
        timestamp_new = self.get_exif_info(photo, folder)
        # MD5 = hashlib.md5(photo)
        logger.info(f'adding mapping and rename for {photo} in {str(folder)}, new name will be timestamp_new')
        self.mapping[photo] = (timestamp_new, folder)
        # os.rename(photo,timestamp_new)

    def loop_folder(self, folder):
        logger.debug(f'looping {folder}')
        os.chdir(folder)
        for photo in os.listdir(folder):
            if os.path.isdir(photo):
                logger.debug(f'{photo} is not a file, will loop inside it')
                self.loop_folder(pathlib.Path(folder / photo))
                os.chdir(folder)
                continue
            self.rename_photo(photo, folder)

    def write_change_log(self):
        logger.info(f'finished {self.count} photos')
        os.chdir(log_folder)
        time_format = '%Y%m%dT%H%M%SZ'
        uct_time_now = datetime.datetime.now(datetime.timezone.utc).strftime(time_format)
        change_file_name = f'changed_files_{uct_time_now}.txt'
        print(os.getcwd())
        with open(change_file_name, 'a', encoding="utf-8") as fh:
            for k, v in p.mapping.items():
                print(k, v)
                fh.write(str(v[1]) + '\t' + k + ' to ' + v[0] + '\n')

    def get_exif_misc(self, image):
        with open(image, 'rb') as image_meta:
            my_meta = Image(image_meta)
        print(type(my_meta))
        print(dir(my_meta))
        print(my_meta.datetime)
        print(my_meta.datetime_original)
        print(my_meta.datetime_digitized)


if __name__ == '__main__':
    project_folder = pathlib.Path(os.getcwd())
    log_folder = pathlib.Path(project_folder / 'log')
    cur_folder = pathlib.Path("d:\\misc\\test_rename_pic")
    if len(sys.argv) > 1:  # and sys.argv[1]:
        cur_folder = pathlib.Path(sys.argv[1])  # photo_path='D:/misc/test_rename_pic')
    p = Pic(cur_folder)
    p.loop_folder(cur_folder)
    print('write log')
    p.write_change_log()

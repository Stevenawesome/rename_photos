import PIL.Image
import PIL.ExifTags
import datetime
import os
import pathlib
import re
from exif import Image
import logging
import sys


def get_exif_misc(image):
    with open(image, 'rb') as image_meta:
        my_meta = Image(image_meta)
    print(type(my_meta))
    print(dir(my_meta))
    print(my_meta.datetime)
    print(my_meta.datetime_original)
    print(my_meta.datetime_digitized)


class GetNewTimestamp:
    def __init__(self):
        self.count = 0
        pass

    def get_exif2(self, image):
        image_handle = PIL.Image.open(image)
        tag_value = {}
        try:
            if not image_handle.getexif():
                logger.error(f'no meta data, return original data')
                return False
            info = image_handle.getexif()
            for tag_id in info:
                tag = PIL.ExifTags.TAGS.get(tag_id,tag_id)
                value = info.get(tag_id)
                if isinstance(value,bytes):
                    try:
                        value = value.decode()
                    except Exception as e:
                        continue
                tag_value[tag] = value
                if 'Date' in tag or 'date' in tag:
                    logger.info(f'{tag} {value}')
            if 'DateTimeOriginal' not in tag_value or 'DateTimeDigitized' not in tag_value or 'DateTime' not in tag_value :
                logger.info('no meta date, using current file date')
                return False
            if 'DateTimeOriginal' in tag_value:
                original_timestamp = tag_value['DateTimeOriginal']
            elif 'DateTimeDigitized' in tag_value:
                original_timestamp = tag_value['DateTimeDigitized']
            else: #if 'DateTime' in tag_value:
                original_timestamp = tag_value['DateTime']
                #file_stat_path = pathlib.Path(image)
                #curtime = datetime.datetime.fromtimestamp(file_stat_path.stat().st_ctime)
                #original_timestamp = curtime.strftime("%Y%m%d_%H%M%S")
            original_timestamp = re.split(':|\t|\n|\s', original_timestamp)
            original_timestamp = ''.join(original_timestamp+['_']+[image]) + '.jpg'
            self.count += 1
            return original_timestamp
        except AttributeError as ate:
            logger.error(f'no attribute {ate}')
        except Exception as e:
            logger.error(f'other error{e}')

    def loop_photos(self, folder):
        logger.info(f'folder is {folder}')
        os.chdir(folder)
        for photo in os.listdir(folder):
            if os.path.isdir(photo):
                logger.warning(f'not file {photo}')
                self.loop_photos(pathlib.Path(folder / photo))
                os.chdir(folder)
                continue
            try:
                timestamp_new = self.get_exif2(photo)
                if timestamp_new:
                    logger.critical(f'old name is {photo}, new name will be {timestamp_new}')
                os.rename(photo,timestamp_new)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    FORMAT = '%(levelname)s %(asctime)-15s %(message)s process is %(process)d logger name %(name)s'  # %(clientip)s %(user)-8s %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger()
    logger.setLevel(int(sys.argv[2]))
    cur_folder = pathlib.Path(sys.argv[1])  # photo_path='D:/misc/test_rename_pic')
    #cur_folder = sys.argv[1]
    os.mkdir(pathlib.Path(cur_folder / 'backup'))
    s = GetNewTimestamp()
    s.loop_photos(cur_folder)
    print(f'finished {s.count} photos')
    logger.info(f'finished {s.count} photos')


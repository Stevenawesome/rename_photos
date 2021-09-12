import PIL.Image
import PIL.ExifTags
import datetime
import os
import pathlib
import re
from exif import Image
import logging

FORMAT = '%(levelname)s %(asctime)-15s %(message)s process is %(process)d logger name %(name)s'# %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
#d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_exif_misc(image):
    with open(image, 'rb') as image_meta:
        my_meta = Image(image_meta)
    #print(my_meta.has_exif)
    print(type(my_meta))
    print(dir(my_meta))
    print(my_meta.datetime)
    print(my_meta.datetime_original)
    print(my_meta.datetime_digitized)


class GetNewTimestamp:
    def __init__(self):
        pass

    def get_exif2(self, image):
        image_handle = PIL.Image.open(image)
        tag_value = {}
        try:
            if not image_handle.getexif():
                #print(f'no meta data, return original data')
                logger.error(f'no meta data, return original data')
                return image
            info = image_handle.getexif()
            #print(f'tag, value is:\n ')
            #print(type(info))
            #print(f'dic {dict(info)}')
            #print(info)
#            for tag, value in info.items():
            for tag_id in info:
                tag = PIL.ExifTags.TAGS.get(tag_id,tag_id)
                value = info.get(tag_id)
#                decoded = PIL.ExifTags.TAGS.get(tag, tag)
                if isinstance(value,bytes):
                    try:
                        value = value.decode()
                    except Exception as e:
                        continue
                tag_value[tag] = value
                if 'Date' in tag or 'date' in tag:
                    #print(f'{tag} {value}')
                    logger.info(f'{tag} {value}')
#            print(tag_value)
            if 'DateTimeOriginal' in tag_value:
                original_timestamp = tag_value['DateTimeOriginal']
            elif 'DateTimeDigitized' in tag_value:
                original_timestamp = tag_value['DateTimeDigitized']
            elif 'DateTime' in tag_value:
                original_timestamp = tag_value['DateTime']
            else:
                #print('no meta date, using file date')
                file_stat_path = pathlib.Path(image)
                #print(file_stat_path.stat())
                curtime = datetime.datetime.fromtimestamp(file_stat_path.stat().st_ctime)
                original_timestamp = curtime.strftime("%Y%m%d_%H%M%S")
            original_timestamp = re.split(':|\t|\n|\s', original_timestamp)
            original_timestamp = ''.join(original_timestamp) + '.jpg'
            #count += 1
            #print(f'we should convert it to {original_timestamp}\n\n')
            return original_timestamp
        except AttributeError as ate:
            #print(f'no attribute {ate}')
            logger.error(f'no attribute {ate}')
        except Exception as e:
            #print(f'other error{e}')
            logger.error(f'other error{e}')

    def loop_photos(self, folder):
        #print(f'folder is {folder}')
        logger.info(f'folder is {folder}')
        os.chdir(folder)
        for photo in os.listdir(folder):
            if os.path.isdir(photo):
                #print(f'not file {photo}')
                logger.error(f'not file {photo}')
                self.loop_photos(pathlib.Path(folder / photo))
                os.chdir(folder)
                continue
            try:
                #print(f'photo is {photo}')
                #logger.info(f'photo name is {photo}')
                timestamp_new = self.get_exif2(photo)
                #print(f'new name will be {timestamp_new}')
                logger.info(f'new name will be {timestamp_new}')
                #os.rename(photo,timestamp_new)
            except Exception as e:
                logger.error(e)
                #print(f'error is {e}')
import sys
if __name__ == '__main__':
    folder = pathlib.Path(sys.argv[1])#photo_path='D:/misc/test_rename_pic')
    s = GetNewTimestamp()
    s.loop_photos(folder)


import PIL.Image
import PIL.ExifTags
import datetime
import os
import pathlib
import re
from exif import Image
import logging
import sys
import hashlib

def get_exif_misc(image):
    with open(image, 'rb') as image_meta:
        my_meta = Image(image_meta)
    print(type(my_meta))
    print(dir(my_meta))
    print(my_meta.datetime)
    print(my_meta.datetime_original)
    print(my_meta.datetime_digitized)


class Pic:
    def __init__(self, folder):
        self.count = 0
        self.folder = folder
        pass

    def get_exif_info(self, image):
        #print(image)
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
                    print(image, tag, value)
                    print(tag_value,'\n\n')
                    logger.info(f'{tag} {value}')
            if 'DateTimeOriginal' not in tag_value and 'DateTimeDigitized' not in tag_value and 'DateTime' not in tag_value :
                logger.info('no meta date, using current file date')
                return False
            if 'DateTimeOriginal' in tag_value:
                original_timestamp = tag_value['DateTimeOriginal']
            elif 'DateTimeDigitized' in tag_value:
                original_timestamp = tag_value['DateTimeDigitized']
            else: #if 'DateTime' in tag_value:
                original_timestamp = tag_value['DateTime']
                logger.critical('fjdkajfdal'+tag_value['DateTime'])
                print(tag_value['DateTime'])
                #file_stat_path = pathlib.Path(image)
                #curtime = datetime.datetime.fromtimestamp(file_stat_path.stat().st_ctime)
                #original_timestamp = curtime.strftime("%Y%m%d_%H%M%S")
            original_timestamp = re.split(':|\t|\n|\s', original_timestamp)
            original_timestamp = ''.join(original_timestamp+['_']+[image]) + '.jpg'
            self.count += 1
            return original_timestamp
        except AttributeError as ate:
            logger.error(f'no attribute {ate}')
            return False
        except Exception as e:
            logger.error(f'other error{e}')
            return False

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
                timestamp_new = self.get_exif_info(photo)
                if timestamp_new:
                    MD5 = hashlib.md5(photo)

                    logger.critical(f'old name is {photo}, new name will be {timestamp_new}')
                    print('adding mapping', photo, timestamp_new, str(folder))
                    mapping[photo] =(timestamp_new, folder)
                #os.rename(photo,timestamp_new)
            except Exception as e:
                logger.error(e)
                continue


if __name__ == '__main__':
    FORMAT = '%(levelname)s %(asctime)-15s %(message)s process is %(process)d logger name %(name)s'  # %(clientip)s %(user)-8s %(message)s'
    logging.basicConfig(filemode='a', format=FORMAT, level=logging.DEBUG)
    handler = logging.FileHandler(sys.argv[0] + ".log", 'a', 'utf-8')

    logger = logging.getLogger()
    #log_level = 50
    #if sys.argv[2]:
    #    logger.setLevel(int(sys.argv[2]))
    #logger.setLevel(int(log_level))
    logger.addHandler(handler)
    cur_folder = pathlib.Path("d:\\misc\\test_rename_pic")
    if len(sys.argv)>1:# and sys.argv[1]:
        cur_folder = pathlib.Path(sys.argv[1])  # photo_path='D:/misc/test_rename_pic')
    #cur_folder = sys.argv[1]
#    os.mkdir(pathlib.Path(cur_folder / 'backup'))
    s = Pic(cur_folder)
    mapping = {}
    s.loop_photos(cur_folder)
    print(f'finished {s.count} photos')
    logger.info(f'finished {s.count} photos')
    print(mapping)
    with open('changed_files.txt', 'a', encoding="utf-8") as fh:
        for k, v in mapping.items():
            print(k, v)
            fh.write(str(v[1]) +'\t' +k +'to'+v[0])


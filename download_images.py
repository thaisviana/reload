import os
import dotenv
from math import ceil
import json
from PIL import Image
from io import BytesIO
import requests
import dropbox
from dropbox.files import WriteMode
import getpass
from blend_images import blend_images
from idna import unicode
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))

size = 70, 70
big_size = 640, 640
root_dropbox_path = '/teste_mul/'
# root_dropbox_path = '/nwjs-v0.38.4-win-x64/public/'
url = 'http://small-big-api.herokuapp.com/photo'
path = '/Users/thaisviana/hub9/auto_reload/imgs/small/'
big_path = '/Users/thaisviana/hub9/auto_reload/imgs/big/'
# path = f'C:/Users/{getpass.getuser()}/Documents/Hub9/auto_reload/dist/reload/imgs/small/'
dbx_path = root_dropbox_path + 'imgs/small/'
dbx_big_path = root_dropbox_path + 'imgs/big/'
dbx = dropbox.Dropbox('9dXiur3lW-AAAAAAAAAAC2DXsDaGJgscGQbQpz1ZOvKAl8pGxNR4Al3CgeSp96LU')
url_postmon = 'http://api.postmon.com.br/v1/cep/'
limit = 100
#path = f'C:/Users/{getpass.getuser()}/Desktop/Hub9/auto_reload/imgs/small/'
#path = '/home/sharmaxz/Documents/hub9/auto_reload/imgs/small'
#dbx_path = '/teste/imgs/small/'


def download_images(small_big):
    img = None
    if not dbx.files_list_folder('').entries:
        dbx.files_create_folder(root_dropbox_path + 'imgs/small')
        dbx.files_create_folder(root_dropbox_path + 'assets/json')

    img_count, img_downloaded, img_response_failed = 0, 0, 0

    shortcode_jpg = small_big['shortcode'] + '.jpg'
    try:
        photo = dbx.files_alpha_get_metadata(f"{dbx_path}{shortcode_jpg}")
    except:
        photo = ''
    try:
        img_count += 1
        if photo == '':
            img_downloaded += 1
            response = requests.get(small_big['image_url'], stream=True)

            if not response.ok:
                img_response_failed += 1
                requests.delete(url + '/delete/' + small_big['shortcode'])
                print(f"The shortcode {small_big['shortcode']} was deleted!")
            else:
                print(small_big['shortcode'])
                img = Image.open(BytesIO(response.content)).convert('RGB')
                big_img = img.copy()

                #insert small photo
                img.thumbnail(size, Image.ANTIALIAS)
                img.save(path + shortcode_jpg, "JPEG")
                with open(path + shortcode_jpg, 'rb') as f:
                    try:
                        dbx.files_upload(f.read(), f"{dbx_path}{shortcode_jpg}", mode=WriteMode('overwrite'))
                        f.close()
                        os.remove(path + shortcode_jpg)
                    except:
                        print("WARNING: uploud failed!", shortcode_jpg)

                #insert big photos
                big_img.thumbnail(big_size, Image.ANTIALIAS)
                big_img.save(big_path + shortcode_jpg, "JPEG")
                with open(big_path + shortcode_jpg, 'rb') as f:
                    try:
                        dbx.files_upload(f.read(), f"{dbx_big_path}{shortcode_jpg}", mode=WriteMode('overwrite'))
                        f.close()
                        os.remove(big_path + shortcode_jpg)
                    except:
                        print("WARNING: uploud failed!", shortcode_jpg)
        else:
            print(f"Image {small_big['shortcode']} already was added")

    except Exception as e:
        if os.path.exists(path + shortcode_jpg):
            os.remove(path + shortcode_jpg)
        print('Unexpected error:' + str(e))

    return img


def image_limiter():
    processed = {"pages": "?", "result": [], "n_lines": 0, "n_columns": 0}
    percentual = {}
    list_images = []

    # with open('location.json', 'r') as file:
    #     result = json.loads(file.read())
    #     images_total = result[0]['Images total']
    #     for zone in result[1:]:
    #         for z in zone:
    #             #
    #             per = ((100 * zone[z][0]['count']) / images_total)
    #             percentual[z] = f"{'%.2f'%(per)}%"
    #
    #             zone_limit = ceil(per * limit / 100)
    #             for small_big in zone[z][1:zone_limit]:
    #                 img = download_images(small_big)
    #                 if img:
    #                     list_images.append((small_big['shortcode'], img))
    #             processed['result'].append(zone[z][1:zone_limit])
    #     map_images = blend_images(list_images)
        # print(map_images)

    with open('original_processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result'][:limit]:
            img = download_images(small_big)
            if img:
                list_images.append((small_big['shortcode'], img))
                processed['result'].append(small_big)
        map_images = blend_images(list_images)

    ordered = sorted(processed['result'], key=lambda x: x['ref_timestamp'], reverse=True)
    processed['result'] = ordered
    n_columns = int(math.sqrt(len(list_images)))
    processed.update({'n_lines': n_columns, 'n_columns': n_columns})
    for json_entry in ordered:
        item = [item for item in map_images if item["shortcode"] == json_entry['shortcode']]
        if item:
            item = item[0]
            json_entry.update({'x': item['x'], 'y': item['y']})
        else:
            ordered.remove(json_entry)

    print("The images were updated!")


    with open('percentual.json', 'w+', encoding='utf8') as file:
        result = json.dumps(percentual, indent=3, ensure_ascii=False)
        file.write(unicode(result))
        file.close()

    with open('processed.json', 'w+', encoding='utf8') as file:
        result = json.dumps(processed, indent=3)
        file.write(result)
        file.close()

    with open('percentual.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'{root_dropbox_path}assets/json/{f.name}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: percentual.json uploud failed!")
        f.close()

    with open('hashtags.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'{root_dropbox_path}assets/json/{f.name}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: hashtags.json uploud failed!")
        f.close()

    with open('processed.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'{root_dropbox_path}assets/json/{f.name}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: processed.json uploud failed!")
        f.close()

    #download_images()
#image_limiter()
from PIL import Image
import math



def blend_images(lista_images):
    n_columns = int(math.sqrt(len(lista_images)))
    n_lines = n_columns
    map_images = []

    images = []

    for count in range(0,n_columns):
        images.append(lista_images[count*n_columns:(count*n_columns)+n_columns])

    # print("%d images will be combined." % len(images))

    image_width, image_height = (70,70)

    # print("all images assumed to be %d by %d." % (image_width, image_height))


    master_width = image_width * n_lines
    #seperate each image with lots of whitespace
    master_height = image_height * n_columns
    # print("the master image will by %d by %d" % (master_width, master_height))
    # print("creating image...")
    master = Image.new(
        mode='RGB',
        size=(master_width, master_height),
        color=(0,0,0))

    # print("created.")

    for index_i, line_images in enumerate(images):
        for index_j, image in enumerate(line_images):
            location_height = image_height * index_i
            location = image_width * index_j
            map_images.append({'shortcode': image[0], 'x': location, 'y': location_height})
            master.paste(image[1], (location, location_height))
            # print("added.")
    # print("done adding icons.")

    # print("saving master.jpg...",)
    # print(map_images)
    master.save('/Users/thaisviana/hub9/auto_reload/imgs/small/small_master.jpg', transparency=0 )

    return map_images
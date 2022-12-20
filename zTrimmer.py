from PIL import ImageGrab, Image, ImageDraw, ImageOps, ImageChops
#from pynput import keyboard
import string
import numpy as np
from io import BytesIO
import win32clipboard
import matplotlib.pyplot as plt
import sys
import time

gridsize = 10

#https://stackoverflow.com/a/62007792
def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

img = ImageGrab.grabclipboard()
print(img)
if isinstance(img, list):
    img = Image.open(img[0])

print(img)
if not img:
    print("Please copy image to clipboard. ")
    time.sleep(1)
    sys.exit()
print(img.mode)

def autocrop_image2(image):
    image.load()
    image_data = np.asarray(image)
    image_data_bw = image_data[:,:,3]
    non_empty_columns = np.where(image_data_bw.max(axis=0) > 0)[0]
    non_empty_rows = np.where(image_data_bw.max(axis=1) > 0)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows),
               min(non_empty_columns), max(non_empty_columns))

    image_data_new = image_data[cropBox[0]:cropBox[
        1] + 1, cropBox[2]:cropBox[3] + 1, :]

    new_image = Image.fromarray(image_data_new)
    return new_image


def gen_checkerboard(w, h, color_bg = (0,0,0), color_fg = (0,255,0)):
    # Please don't question the color scheme :)
    # https://stackoverflow.com/a/54411453
    # Create new black image of entire board
    img = Image.new("RGBA", (w,h), color=color_bg)
    pixels = img.load()

    # Make pixels white where (row+col) is odd
    for i in range(w):
        for j in range(h):
            if (i+j)%2:
                pixels[i,j] = color_fg
    return img
                
                



# https://stackoverflow.com/a/35859141
def remove_transparency(im, bg_colour=(255, 255, 255)):
    # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
    alpha = im.convert('RGBA').split()[-1]

    # Create a new background image of our matt color.
    # Must be RGBA because paste requires both images have the same format
    # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
    bg = Image.new("RGBA", im.size, bg_colour + (255,))
    bg.paste(im, mask=alpha)
    return bg
        
def check_img_transparency(im):
    # http://stackoverflow.com/a/1963146
    return (im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info))


logallpress_key = None

def logallpress(event):
    global logallpress_key
    if event is None:
        logallpress_key = "b"
    else:
        logallpress_key = event.key
    plt.close()


# https://stackoverflow.com/a/56280735
if check_img_transparency(img) and ImageChops.difference(img.convert("RGBA"), remove_transparency(img.convert("RGBA"))).getbbox():
    img_checkerboard = gen_checkerboard(img.size[0]//gridsize,img.size[1]//gridsize)
    img_checkerboard = img_checkerboard.resize((img_checkerboard.size[0]*gridsize,img_checkerboard.size[1]*gridsize), Image.Resampling.NEAREST)
    img_checkerboard = ImageOps.pad(img_checkerboard, img.size, color=(0,0,0))
    img_checkerboard.paste(img, (0, 0), img)
    #img_checkerboard.show()
    fig, ax = plt.subplots(num='1:[B]lack / 2:[W]hite / 3:[H]ex / 4:[R]GB / 5:[T]rim only')
    fig.canvas.mpl_connect("key_press_event",logallpress)
    previewplot = plt.imshow(img_checkerboard)
    plt.title("1:[B]lack / 2:[W]hite / 3:[H]ex / 4:[R]GB / 5:[T]rim only")
    plt.show()
    
    usrkey = logallpress_key
    
    '''with keyboard.Events() as events:
        event = events.get(100)
        if event is None:
            usrkey = "b"
        else:
            usrkey = event.key.char'''
    if usrkey in "5t":
        img = autocrop_image2(img)
        #img.show()
        # https://stackoverflow.com/a/74568786
        buffer = BytesIO()
        img.save(fp=buffer, format='PNG')

        clipboard_format = win32clipboard.RegisterClipboardFormat('PNG')
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clipboard_format, buffer.getvalue())
        win32clipboard.CloseClipboard()

        buffer.close()
        sys.exit()
    if usrkey in "1b":
        bg_colour = (0, 0, 0)
    elif usrkey in "2w":
        bg_colour = (255, 255, 255)
    elif usrkey in "3h":
        # https://stackoverflow.com/a/29643643
        h = input('Hex: ').lstrip("h").lstrip('#')
        bg_colour = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    elif usrkey in "4r":
        usrinput = input("RGB: ").lstrip("r")
        if len(usrinput.split(",")) == 3:
            bg_colour = tuple(int(substr.strip(string.ascii_letters)) for substr in usrinput.split(","))
        else:
            bg_colour = tuple(int(usrinput[i:i+3]) for i in (0, 3, 6))
    #print(usrkey)
    #print(bg_colour)
    img = remove_transparency(img, bg_colour)
    
    
    
    
img = img.convert("RGB")
img_orig = img.copy()
#print(img_orig)
#print("/\ img_orig")

    
    
    
'''

for i_coord in range(4):
    coords = [(0,0), (0,img.size[1]), (img.size[0],0), (img.size[0],img.size[1])]
    img_copy = img.copy()
    img_copy = img_copy.convert("RGB")
    print(img_copy.mode)
    #img_arr = np.asarray(img_copy)
    print(coords[i_coord])
    ImageDraw.floodfill(img_copy, coords[i_coord], (0,0,0), thresh=0)
    #cv2.floodFill(img_arr, None, seedPoint=coords[i_coord], newVal=(0,0,0), loDiff=(0, 0, 0), upDiff=(0, 0, 0))
    #img_copy = Image.fromarray(img_arr)
    crop_bbox = img_copy.getbbox()
    print(crop_bbox)
    img = img.crop(crop_bbox)'''

def crop_image(img, coord):
    img_copy = img.copy()
    img_copy = img_copy.convert("RGB")
    #print(img_copy.mode)
    #img_arr = np.asarray(img_copy)
    #print(coords[i_coord])
    ImageDraw.floodfill(img_copy, coord, (0,0,0), thresh=0)
    #cv2.floodFill(img_arr, None, seedPoint=coords[i_coord], newVal=(0,0,0), loDiff=(0, 0, 0), upDiff=(0, 0, 0))
    #img_copy = Image.fromarray(img_arr)
    crop_bbox = img_copy.getbbox()
    #print(crop_bbox)
    img = img.crop(crop_bbox)
    return img

# https://stackoverflow.com/a/10616717

def trim(im, seed):
    bg = Image.new(im.mode, im.size, im.getpixel(seed))
    diff = ImageChops.difference(im, bg)
    #diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

confirm_key = None

def press(event):
    global img
    global img_copy
    global confirm_key
    #print('press', event.key)
    if event.key in ".":
        if not confirm_key == ".":
            confirm_key = "."
            plt.title("Press [.] again to quit without saving.")
            plt.draw()
            return
        else:
            sys.exit()
    elif str(event.key) == "enter": 
        if not confirm_key == str(event.key):
            confirm_key = str(event.key)
            plt.title("Press [Enter] again to save image.")
            plt.draw()
            return
        else:
            output = BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            send_to_clipboard(win32clipboard.CF_DIB, data)
            sys.exit()
    confirm_key = None
    plt.title("[Enter]: save. [.]: quit without saving. ")
    if event.key in "1379":
        coords = [(0,0), (0,img.size[1]-1), (img.size[0]-1,0), (img.size[0]-1,img.size[1]-1)]
        lookup = {1: 1, 7:0, 9:2, 3:3}
        #print(coords[lookup[int(event.key)]])
        #img = crop_image(img, coords[lookup[int(event.key)]])
        img2 = trim(img, coords[lookup[int(event.key)]])
        if img2:
            img = img2
        else: 
            print("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
            plt.title("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
        '''plt.close()
        fig, ax = plt.subplots()
        fig.canvas.mpl_connect("key_press_event",press)
        imgplot = plt.imshow(img)
        plt.show()'''
        #imgplot.set_data(img)
        ax.imshow(img)
        plt.draw()
        #plt.show()
    elif event.key in "5":
        for coord_i in range(4):
            coords = [(0,0), (0,img.size[1]-1), (img.size[0]-1,0), (img.size[0]-1,img.size[1]-1)]
            #print(coords)
            img2 = trim(img, coords[coord_i])
            if img2:
                img = img2
            else: 
                print("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
                plt.title("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
        ax.imshow(img)
        plt.draw()
    elif event.key in "-":
        img = img_orig.copy()
        ax.imshow(img)
        plt.draw()
    elif event.key in "8":
        img_arr = np.asarray(img)
        truth = np.all(np.all(img_arr == (img_arr[0]), axis=1), axis=1)
        #print(truth)
        for i in range(1,img_arr.shape[0]): # assuming 0th and 1st equal, can surefire trim at least 1 pixel. 
            if truth[i]: # if np.equal(img_arr[0],img_arr[i]).all():
                pass
            else:
                break
        # i-th and 0-th not equal, i-1-th equal. But we trim one more
        try:
            img_arr = img_arr[i-1+1:]
        except:
            print("Image just 1 pixel tall!!!")
            plt.title("Image just 1 pixel tall!!!")
        img = Image.fromarray(img_arr)
        ax.imshow(img)
        plt.draw()
    elif event.key in "2":
        img_arr = np.asarray(img)
        truth = np.all(np.all(img_arr == (img_arr[-1]), axis=1), axis=1)
        #print(truth)
        for i in range(2,img_arr.shape[0]+1): # assuming -1th and -2st equal, can surefire trim at least 1 pixel. 
            if truth[-i]: #if np.equal(img_arr[-1],img_arr[-i]).all():
                pass
            else:
                break
        # But we trim one more
        try:
            img_arr = img_arr[:-(i-1-1+1)]
        except:
            print("Image just 1 pixel tall!!!")
            plt.title("Image just 1 pixel tall!!!")
        img = Image.fromarray(img_arr)
        ax.imshow(img)
        plt.draw()
    elif event.key in "4":
        img_arr = np.asarray(img).swapaxes(0,1) # same logic as 8
        truth = np.all(np.all(img_arr == (img_arr[0]), axis=1), axis=1)
        #print(truth)
        for i in range(1,img_arr.shape[0]): # assuming 0th and 1st equal, can surefire trim at least 1 pixel. 
            if truth[i]: #if np.equal(img_arr[0],img_arr[i]).all():
                pass
            else:
                break
        # i-th and 0-th not equal, i-1-th equal
        try:
            img_arr = img_arr[i-1+1:]
        except:
            print("Image just 1 pixel wide!!!")
            plt.title("Image just 1 pixel wide!!!")
        img = Image.fromarray(img_arr.swapaxes(0,1))
        ax.imshow(img)
        plt.draw()
    elif event.key in "6":
        img_arr = np.asarray(img).swapaxes(0,1) # same logic as 2
        truth = np.all(np.all(img_arr == (img_arr[-1]), axis=1), axis=1)
        #print(truth)
        for i in range(2,img_arr.shape[0]+1): # assuming -1th and -2st equal, can surefire trim at least 1 pixel. 
            if truth[-i]: #if np.equal(img_arr[-1],img_arr[-i]).all():
                pass
            else:
                break
        # i-th and 0-th not equal, i-1-th equal
        try:
            img_arr = img_arr[:-(i-1-1+1)]
        except:
            print("Image just 1 pixel wide!!!")
            plt.title("Image just 1 pixel wide!!!")
        img = Image.fromarray(img_arr.swapaxes(0,1))
        ax.imshow(img)
        plt.draw()

    #print(str(event.key))




    

    



fig, ax = plt.subplots(num='[Enter]: save. [.]: quit without saving. ')
fig.canvas.mpl_connect("key_press_event",press)
imgplot = plt.imshow(img)
plt.title("[Enter]: save. [.]: quit without saving. ")
plt.show()
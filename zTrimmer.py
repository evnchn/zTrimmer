import io
import os
import PySimpleGUI as sg
import sys
from PIL import Image, ImageTk, ImageOps, ImageGrab, ImageChops
import time
import numpy as np
from io import BytesIO
import win32clipboard
import webbrowser
import string
import ctypes
import platform


def make_dpi_aware():
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        
make_dpi_aware()
try:
    os.mkdir("output")
except:
    pass


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

# GUI #


layout = [

        [sg.Image(key='-IMAGE-', pad=(0, 0))]
         ]
         

window = sg.Window('Loading...', layout, return_keyboard_events=True, finalize = True, element_justification='c', margins=(0,0), background_color = "#64778d")
window.Maximize()
#print(window.size)



def loadimage(PIL_im, mode=True):
    global window
    if mode:
        ratio = min(window.size[0]//PIL_im.size[0], window.size[1]//PIL_im.size[1])
        #print(ratio)
        ratio = int(ratio)
        if ratio:
            #print(PIL_im.size[0]*ratio,PIL_im.size[1]*ratio)
            #print(window.size)
            PIL_im = PIL_im.resize((PIL_im.size[0]*ratio,PIL_im.size[1]*ratio), resample=Image.Resampling.NEAREST)
            #PIL_im = ImageOps.pad(PIL_im, window.size, color="#FF0000")
            #print(PIL_im.size)
            #print("Done")
            #image = ImageTk.PhotoImage(image=PIL_im)
            # update image in sg.Image
            #window['-IMAGE-'].update(data=image)
            #return
    else:
        PIL_im = ImageOps.contain(PIL_im, window.size)
    
    PIL_im = ImageOps.pad(PIL_im, window.size, color="#64778d")
    # Convert im to ImageTk.PhotoImage after window finalized
    image = ImageTk.PhotoImage(image=PIL_im)
    # update image in sg.Image
    window['-IMAGE-'].update(data=image)
    return
    
    
'''link = 'tutorial.png'
im = Image.open(link)
loadimage(im)'''





for key in list(set("bwhrtBWHRT0123456789/*-+.,abcdefABCDEF")):
    window.bind(key, "-NUMPAD-{}-".format(key))
window.bind("<Escape>", "-ESCAPE-")
window.bind("<Return>", "-ENTER_KEY-")
window.bind("<BackSpace>", "-BACKSPACE-")

gridsize = 10

#https://stackoverflow.com/a/62007792
def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()
    


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


def gen_checkerboard(w, h, color_bg = (0,0,0), color_fg = (0,255,0), parity = 0):
    # Please don't question the color scheme :)
    # https://stackoverflow.com/a/54411453
    # Create new black image of entire board
    img = Image.new("RGBA", (w,h), color=color_bg)
    pixels = img.load()
    parity %= 2
    # Make pixels white where (row+col) is odd
    for i in range(w):
        for j in range(h):
            if (i+j)%2 == parity:
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




if check_img_transparency(img) and ImageChops.difference(img.convert("RGBA"), remove_transparency(img.convert("RGBA"))).getbbox():
    parity = 0
    color_palette = ((0,0,0),(0,255,0))
    img_checkerboard = gen_checkerboard(img.size[0]//gridsize,img.size[1]//gridsize, color_bg = color_palette[0], color_fg = color_palette[1], parity=parity)
    img_checkerboard = img_checkerboard.resize((img_checkerboard.size[0]*gridsize,img_checkerboard.size[1]*gridsize), Image.Resampling.NEAREST)
    img_checkerboard = ImageOps.pad(img_checkerboard, img.size, color=color_palette[0])
    img_checkerboard.paste(img, (0, 0), img)
    loadimage(img_checkerboard)

    window.TKroot.title("1:[B]lack / 2:[W]hite / 3:[H]ex / 4:[R]GB / 5:[T]rim only / 6:[-] Open output")
    get_keyboard = ""
    capture_mode = None
    
    while True:
        event, values = window.read(timeout=0)
        print(event)
        if event in (sg.WIN_CLOSED, '_EXIT_', 'Close'):
            sys.exit()
        if capture_mode == "Hex" and "-NUMPAD-" in event:
            key = event[8]
            get_keyboard += key
            window.TKroot.title("{}: {}".format(capture_mode, get_keyboard))
            if len(get_keyboard) == 6:
                # https://stackoverflow.com/a/29643643
                get_keyboard = get_keyboard.upper()
                bg_colour = tuple(int(get_keyboard[i:i+2], 16) for i in (0, 2, 4))
                break
        elif capture_mode == "RGB" and "-NUMPAD-" in event:
            key = event[8]
            if key not in "0123456789":
                key = ","
            get_keyboard += key
            window.TKroot.title("{}: {}".format(capture_mode, get_keyboard))
            if len(get_keyboard.split(",")) == 4:
                bg_colour = tuple(int(substr.strip(string.ascii_letters)) for substr in get_keyboard.split(","))[:3]
                break
            elif len(get_keyboard) == 9 and get_keyboard.isdigit():
                bg_colour = tuple(int(get_keyboard[i:i+3]) for i in (0, 3, 6))
                break
        elif capture_mode and event == "-BACKSPACE-":
            get_keyboard = get_keyboard[:-1]
            window.TKroot.title("{}: {}".format(capture_mode, get_keyboard))
        else:
            if event in ("-NUMPAD-{}-".format(5),"-NUMPAD-{}-".format("t"),"-NUMPAD-{}-".format("T")):
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
            if event in ("-NUMPAD-{}-".format(1),"-NUMPAD-{}-".format("b"),"-NUMPAD-{}-".format("B")):
                bg_colour = (0, 0, 0)
                break
            elif event in ("-NUMPAD-{}-".format(2),"-NUMPAD-{}-".format("w"),"-NUMPAD-{}-".format("W")):
                bg_colour = (255, 255, 255)
                break
            elif event in ("-NUMPAD-{}-".format(3),"-NUMPAD-{}-".format("h"),"-NUMPAD-{}-".format("H")):
                capture_mode = "Hex"
                window.TKroot.title("{}: {}".format(capture_mode, get_keyboard))
            elif event in ("-NUMPAD-{}-".format(4),"-NUMPAD-{}-".format("r"),"-NUMPAD-{}-".format("R")):
                capture_mode = "RGB"
                window.TKroot.title("{}: {}".format(capture_mode, get_keyboard))
            elif event in ("-NUMPAD-{}-".format(6),"-NUMPAD-{}-".format("-")):
                webbrowser.open("output")
                sys.exit()
            elif event in ("-NUMPAD-{}-".format(0),):
                print("Flip parity")
                print(parity)
                parity += 1
                parity %= 2
                color_palette = ((0,0,0),(0,255,0))
                img_checkerboard = gen_checkerboard(img.size[0]//gridsize,img.size[1]//gridsize, color_bg = color_palette[0], color_fg = color_palette[1], parity=parity)
                img_checkerboard = img_checkerboard.resize((img_checkerboard.size[0]*gridsize,img_checkerboard.size[1]*gridsize), Image.Resampling.NEAREST)
                img_checkerboard = ImageOps.pad(img_checkerboard, img.size, color=(0,0,0))
                img_checkerboard.paste(img, (0, 0), img)
                loadimage(img_checkerboard)
            elif event in ("-NUMPAD-{}-".format("."),):
                print("Flip parity")
                print(parity)
                parity += 1
                parity %= 2
                color_palette = ((255,255,255),(204,204,204))
                img_checkerboard = gen_checkerboard(img.size[0]//gridsize,img.size[1]//gridsize, color_bg = color_palette[0], color_fg = color_palette[1], parity=parity)
                img_checkerboard = img_checkerboard.resize((img_checkerboard.size[0]*gridsize,img_checkerboard.size[1]*gridsize), Image.Resampling.NEAREST)
                img_checkerboard = ImageOps.pad(img_checkerboard, img.size, color=(0,0,0))
                img_checkerboard.paste(img, (0, 0), img)
                loadimage(img_checkerboard)
    print("removing transparency")
    img = remove_transparency(img, bg_colour)
    #img.show()
    #window.close()
    # sys.exit() # debug
img = img.convert("RGB")
img_orig = img.copy()

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
        
def trim_bbox(im, seed):
    bg = Image.new(im.mode, im.size, im.getpixel(seed))
    diff = ImageChops.difference(im, bg)
    #diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox), bbox
        
        
        
confirm_key = None

history = []

phantom_crop_box = [0, 0, img.size[0], img.size[1]]

def phantom_crop(bbox):
    global phantom_crop_box
    global image
    #croponce = (a,b,c,d)

    #croptwice = (i,j,k,l)

    #croptotal = (a+i,b+j,c-a+k, d-b+l)
    
    a,b,c,d = phantom_crop_box
    i,j,k,l = bbox
    
    phantom_crop_box = [a+i,b+j,k+a, l+b]
    
    


loadimage(img)
window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
while True:
    event, values = window.read(timeout=0)
    if event in (sg.WIN_CLOSED, '_EXIT_', 'Close'):
        sys.exit()
    if event in ("-NUMPAD-{}-".format("."),):
        if not confirm_key == ".":
            confirm_key = "."
            window.TKroot.title("[.]: Quit without saving, [-]: Open output")
            continue
        else:
            window.close()
            sys.exit()
    elif event in ("-ENTER_KEY-",): 
        #print("Enter event")
        if not confirm_key == "enter":
            confirm_key = "enter"
            window.TKroot.title("[Enter]: Clipboard, [+]: Browser, [-]: File")
            continue
        else:
            output = BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            send_to_clipboard(win32clipboard.CF_DIB, data)
            window.close()
            sys.exit()
            
    elif event in ("-NUMPAD-{}-".format("+"),) and confirm_key == "enter":
        try:
            os.mkdir("output")
        except:
            pass
        filename = f'{time.strftime("%Y%m%d-%H%M%S")}'
        img.convert("RGB").save("output/{}.png".format(filename),"PNG")
        with open("output/{}.html".format(filename),"w") as ht:
            ht.write("""<html><body><img src="{}"></body></html>""".format("{}.png".format(filename)))
        #print(os.path.realpath(filename))
        webbrowser.open(os.path.realpath("output/{}.html".format(filename)))
        sys.exit()
    elif event in ("-NUMPAD-{}-".format("-"),) and confirm_key == "enter":
        try:
            os.mkdir("output")
        except:
            pass
        filename = f'{time.strftime("%Y%m%d-%H%M%S")}'
        img.convert("RGB").save("output/{}.png".format(filename),"PNG")
        with open("output/{}.html".format(filename),"w") as ht:
            ht.write("""<html><body><img src="{}"></body></html>""".format("{}.png".format(filename)))
        #print(os.path.realpath(filename))
        #webbrowser.open(os.path.realpath("output/{}.html".format(filename)))
        webbrowser.open("output")
        sys.exit()
    elif event in ("-NUMPAD-{}-".format("-"),) and confirm_key == ".":
        webbrowser.open("output")
        sys.exit()
    if event in ("-NUMPAD-{}-".format("1"),"-NUMPAD-{}-".format("3"),"-NUMPAD-{}-".format("7"),"-NUMPAD-{}-".format("9")):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        coords = [(0,0), (0,img.size[1]-1), (img.size[0]-1,0), (img.size[0]-1,img.size[1]-1)]
        lookup = {1: 1, 7:0, 9:2, 3:3}
        #print(coords[lookup[int(event.key)]])
        #img = crop_image(img, coords[lookup[int(event.key)]])
        keynumber = int(event[8])
        img2, bbox = trim_bbox(img, coords[lookup[int(keynumber)]])
        if img2:
            history.append(phantom_crop_box)
            img = img2
            phantom_crop(bbox)
            
            print(history)
        else: 
            print("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
            window.TKroot.title("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
        loadimage(img)
    elif event in ("-NUMPAD-{}-".format("5"),):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        for coord_i in range(4):
            coords = [(0,0), (0,img.size[1]-1), (img.size[0]-1,0), (img.size[0]-1,img.size[1]-1)]
            #print(coords)
            img2, bbox = trim_bbox(img, coords[coord_i])
            if img2:
                img = img2
                history.append(phantom_crop_box)
                phantom_crop(bbox)
                
                print(history)
            else: 
                print("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
                window.TKroot.title("Image is a same-colored patch. Cropping will yield 0 pixels!!!")
        loadimage(img)
    elif event in ("-NUMPAD-{}-".format("-"),):
        print("- pressed")
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        if not history:
            img = img_orig.copy()
            phantom_crop_box = [0, 0, img.size[0], img.size[1]]

            loadimage(img)
        else:
            print("Old:",history)
            oldcropbox = history.pop()
            img = img_orig.crop(oldcropbox)
            phantom_crop_box = oldcropbox
            loadimage(img)
            print("New:",history)
    elif event in ("-NUMPAD-{}-".format("8"),):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        if img.size[1] > 1:
            confirm_key = None
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
                history.append(list(phantom_crop_box))
                phantom_crop_box[1] += i
                print(phantom_crop_box)
            except Exception as e:
                print(e)
                print("Image just 1 pixel tall!!!")
                window.TKroot.title("Image just 1 pixel tall!!!")
            img = Image.fromarray(img_arr)
            loadimage(img)
        else:
            print("Image just 1 pixel tall!!!")
            window.TKroot.title("Image just 1 pixel tall!!!")
    elif event in ("-NUMPAD-{}-".format("2"),):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        if img.size[1] > 1:
            confirm_key = None
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
                history.append(list(phantom_crop_box))
                phantom_crop_box[3] -= (i-1)
                print(phantom_crop_box)
            except:
                print("Image just 1 pixel tall!!!")
                window.TKroot.title("Image just 1 pixel tall!!!")
            img = Image.fromarray(img_arr)
            loadimage(img)
        else:
            print("Image just 1 pixel tall!!!")
            window.TKroot.title("Image just 1 pixel tall!!!")
    elif event in ("-NUMPAD-{}-".format("4"),):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        if img.size[0] > 1:
            confirm_key = None
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
                history.append(list(phantom_crop_box))
                phantom_crop_box[0] += i
                print(phantom_crop_box)
            except:
                print("Image just 1 pixel wide!!!")
                window.TKroot.title("Image just 1 pixel wide!!!")
            img = Image.fromarray(img_arr.swapaxes(0,1))
            loadimage(img)
        else:
            print("Image just 1 pixel wide!!!")
            window.TKroot.title("Image just 1 pixel wide!!!")
    elif event in ("-NUMPAD-{}-".format("6"),):
        window.TKroot.title("[Enter]: save. [.]: quit. [-]: undo.")
        confirm_key = None
        if img.size[0] > 1:
            confirm_key = None
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
                history.append(list(phantom_crop_box))
                phantom_crop_box[2] -= (i-1)
                print(phantom_crop_box)
            except:
                print("Image just 1 pixel wide!!!")
                window.TKroot.title("Image just 1 pixel wide!!!")
            img = Image.fromarray(img_arr.swapaxes(0,1))
            loadimage(img)
        else:
            print("Image just 1 pixel wide!!!")
            window.TKroot.title("Image just 1 pixel wide!!!")
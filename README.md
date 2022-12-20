# zTrimmer

> In the time you need to open PhotoShop, I have trimmed my images 6 times already. 

A quick way to trim and handle images in the clipboard. 

## Uses

- Force a bitmap clipboard 
  - If you paste from Photoshop to PowerPoint, it embeds some sort of image object and the styling and positioning options are limited.
  - You can remediate this by pasting to Paint first, but this is very troublesome. 
- Ensure consistent padding when performing layout of images, where the image is guaranteed not to have internal padding. 
- Flatten transparent image to black
  - If you copy transparent image and get all black / all white / little contrast, flattening to another color may help, but you cannot choose to what color under native Windows.
- Extract Excel cells as images without the nasty border. 

## Installation

This is still in early beta so no installer is provided. Please install all dependencies in the top of the zTrimmer.py file, then using other software such as AutoHotKey, map a certain hotkey to launch this script (no command-line arguments needed nor accepted). 

## Learning how to use

I personally recommend playing around with tutorial.png and try to experiment with the on-screen instructions and numberpad buttons until one reaches the image in tutorial-destination.png
The controlls are intuitive once you learnt to use them. 

## Instructions

1. Copy image to clipboard / copy image file to clipboard (PNG/BMP highly recommended)
   - Only works with images with lossless compression for now. Does not work with JPEGs very well. 
2. Launch zTrimmer.py
3. Refer to the on-screen instructions: **1:[B]lack / 2:[W]hite / 3:[H]ex / 4:[R]GB / 5:[T]rim only**
   - If the image is transparent, you may press **5/T** to Trim the image according to the minimum bounding box of non-transparent images {Photoshop -> Image -> Trim -> Based on Transparent Pixels}. 
   - Alternatively, you can press **1/B or 2/W** to flatten to black or white, or press **3/H or 4/R** and enter Hex values and RGB values respectively. 
   - For Hex values, # prefixes are always ignored and does not matter whether it is there or not. 
     - ```#FF00FF``` and ```FF00FF``` both works
   - For RGB values, anything with 2 commas will be accepted, such as ```rgb(255,0,255)```, ```255,0,255```. 
     - You may also enter RGB values with 3-digit channel values, such as ```255000255```, which is also accepted here. 
4. The trimming interface accepts keypresses assuming a numberpad layout. 
   - 1, 7, 9, 3: Trims image of area same color as the corresponding corner
     - Same as {Photoshop -> Image -> Trim -> Based on XXX Pixel Color}
     - If the image is of a same color, trimming would leave zero pixels behind. Therefore there will be no change. 
   - 2, 4, 8, 6: Trims the image beginning from the edge until the row/column of pixels is different. 
     - If there is nothing to crop, it would still always crop 1 row/column of pixels. 
       - This helps with cropping some pixtures with antialiased features. 
     - If the image is of a same color, this would leave a single pixel wide/tall image. 
   - 5: currently performs keypress 7 1 9 3
   - . [Dot]: Press twice to quit without saving
   - [Enter]: Press twice to copy result back to clipboard
   

 

## Compatibility 

**Works on Windows only** for now, as it relies on win32clipboard. Code can be modified but I do not have any devices to test

## Todos

- Migrate to a GUI library instead of forcing matplotlib to do what I want. 
- Improve speed when handling images of larger size. 

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

## Instructions (for PySimpleGUI latest version)

1. Copy image to clipboard / copy image file to clipboard (PNG/BMP highly recommended)
   - Only works with images with lossless compression for now. Does not work with JPEGs very well. 
2. Launch zTrimmer.py
3. For transparent images, refer to the on-screen instructions on the title bar: **1:[B]lack / 2:[W]hite / 3:[H]ex / 4:[R]GB / 5:[T]rim only / 6:[-] Open output**
   - You may press <kbd>5</kbd>/<kbd>T</kbd> to Trim the image according to the minimum bounding box of non-transparent images {Photoshop -> Image -> Trim -> Based on Transparent Pixels}. 
   - You may press <kbd>6</kbd>/<kbd>-</kbd> which opens the output folder. 
   - Alternatively, you can press <kbd>1</kbd>/<kbd>B</kbd> or <kbd>2</kbd>/<kbd>W</kbd> to flatten to black or white, or press <kbd>3</kbd>/<kbd>H</kbd> or <kbd>4</kbd>/<kbd>R</kbd> and enter Hex values and RGB values respectively. 
   - For Hex values, # prefixes simply cannot be entered. (e.g. ```FF00FF```)
   - For RGB values, anything with 3 commas will be accepted, such as ```255,0,255,```. Other non-numeric characters always treated as comma. 
     - You may also enter RGB values with 3-digit channel values, such as ```255000255```, which is also accepted here. 
4. The trimming interface accepts keypresses assuming a numberpad layout. 
   - <kbd>1</kbd>, <kbd>7</kbd>, <kbd>9</kbd>, <kbd>3</kbd>: Trims image of area same color as the corresponding corner
     - Same as {Photoshop -> Image -> Trim -> Based on XXX Pixel Color}
     - If the image is of a same color, trimming would leave zero pixels behind. Therefore there will be no change. 
   - <kbd>2</kbd>, <kbd>4</kbd>, <kbd>8</kbd>, <kbd>6</kbd>: Trims the image beginning from the edge until the row/column of pixels is different. 
     - If there is nothing to crop, it would still always crop 1 row/column of pixels. 
       - This helps with cropping some pixtures with antialiased features. 
     - If the image is of a same color, this would leave a single pixel wide/tall image. 
   - <kbd>5</kbd>: currently performs keypress 7 1 9 3
   - <kbd>.</kbd>-><kbd>.</kbd>: Press twice to quit without saving
   - <kbd>Enter</kbd>-><kbd>Enter</kbd>: Press twice to copy result back to clipboard
   - <kbd>Enter</kbd>-><kbd>+</kbd>: Opens the browser for easier Google Image Search / Bing Image Search
   - <kbd>Enter</kbd>-><kbd>-</kbd>: Opens the output folder for easier image uploading
   - <kbd>-</kbd>: **Undo**
   

 

## Compatibility 

**Works on Windows only** for now, as it relies on win32clipboard. Code can be modified but I do not have any devices to test

## Todos

- Migrate to a GUI library instead of forcing matplotlib to do what I want. 
- Improve speed when handling images of larger size. 

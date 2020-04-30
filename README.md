# Raspberry Pi camera long exposure
Python3 program for Raspberry Pi camera long exposure captures at night. One of my hobby/interests is capturing night sky images. I had been using the Meteotux PI program by Jani Lappalainen to capture meteors, satellites, stars, and lots of planes over the light polluted skys of northern NJ. I had wanted to get a better understanding of how the Raspberry Pi camera operated so implemented a version in python.

## Getting Started
You can use git to clone this project or download the ZIP and install it manually.

## Prerequisites
You will need the following to use run this program:
 * a Raspberry pi with CSI camera interface (Raspberry Pi Zero W)
 * Raspbian Stretch or later installed
 * a Raspberry pi camera (developed with v2 NoIR)
 * python3 installed (developed with 3.5.3)
 * python3-picamera package installed (see https://picamera.readthedocs.io/en/release-1.13/install.html)

## Usage
usage: rpicamle.py [-h] [-d DURATION] [-e EXPOSURE] [-f FILEPREFIX]
                   [-drc {off,low,medium,high}] [-v]

optional arguments:

  -h, --help            show this help message and exit

  -d DURATION, --duration DURATION
                        Duration of image in seconds, default is 60

  -e EXPOSURE, --exposure EXPOSURE
                        Camera exposure time in milliseconds, default is 5000

  -f FILEPREFIX, --fileprefix FILEPREFIX
                        Text added in front of filename, default is './img'

  -drc {off,low,medium,high}
                        Dynamic range compression, default is 'off'

  -v, --verbose         Print verbose logging


python3 rpicamle.py -e 5000 -d 60

Take 5000 msec exposures and generate at stacked image every 60 seconds.  These are the default settings.


## Details (how it works)
I had planned to use the Raspberry pi raspistill utility. However, I found that it caused too much delay between each image capture. Not so much of an issue for capturing slow moving stars, but it caused gaps for faster moving objects (satellites and planes). It also would miss anything that happen to occur between images (meteors).

After much searching and experimentation, I settled on the approach used in rpicamle, using the picamera.capture_sequence() function (interestingly not capture_continuous) and an exposure time of 5 seconds. The V1 Picamera has a limit of 6 seconds for maximum exposure time, while V2 camera supports up to 10 second exposures. One issue I found is that the camera takes longer to provide an image as the exposure time increases. With the V2 camera, 5 second exposures take ~ 20msec while 10 second exposures are 250msec. 

With the longest exposure limited to 10 second images, the next hurdle is how to save the data. 10 second images, 6 images per minute, 360 images per hour, would be tedious (and rough on the sd card) to generate that many files. To get around this, rpicamle uses the python numpy array package numpy.maximum function to stack individual images into a single jpg file. The numpy.maximum function takes 2 images as input, generating a new image using the "brightest" pixel for each position in an image. Images are stacked until the duration is reached. The stacked image is written to disk and a new stack is started.

## Caveats
Clouds. Clouds cause two issues. They obscure the sky and move across the viewing area. They are also generally brighter than the stars we are attempting to capture, causing the numpy process to use the cloud pixels rather than the sky/star pixels. End result is loss of the sky image data.

Capturing faint objects. The maximum exposure time limits the amount of visual light data the raspberry pi camera can capture. Its also impacted by light pollution in your area.  General rule, the darker location you are in, the better the images will be.

## Scripts/Tools
I've included some scripts and examples to aid in post processing the set of captured images.

### Copy files from Raspberry pi to local drive (Linux)
rsync -av pi@192.168.1.65:/home/pi/rpicamle/20200428/*  /home/tim/Pictures/20200428/

### Stack recorded images to single stacked image (great for star trails)
Stacks all files that match 'img*.jpg' in current directory, saved to stacked_image.jpg

python3 stack.py

### Create video using ffmpeg from images
for f in ./*.jpg ; do echo "file $f" ; done > filenames.txt

ffmpeg -f concat -r 8 -safe 0 -i filenames.txt -b:v 2m -vcodec mjpeg 20200428.mp4



## Author / Contributing
Timothy Vitz

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT license](https://choosealicense.com/licenses/mit/)

## Acknowledgments
Inspired by Meteotux PI by Jani Lappalainen

https://sites.google.com/site/meteotuxpi/home

rpicamle would not be possible without additional input from the following:

https://www.raspberrypi.org/forums/viewtopic.php?t=220544

https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

https://jmlb.github.io/robotics/2017/11/22/picamera_streaming_video/

https://picamera.readthedocs.io/en/release-1.13/

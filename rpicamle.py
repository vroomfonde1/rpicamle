#!/usr/bin/env python3
"""
Python3 program for Raspberry Pi camera long exposure night captures
Code derived from discussion https://www.raspberrypi.org/forums/viewtopic.php?t=220544
https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
https://jmlb.github.io/robotics/2017/11/22/picamera_streaming_video/
https://picamera.readthedocs.io/en/release-1.13/
Inspired by
https://sites.google.com/site/meteotuxpi/home
"""

import picamera
import picamera.array
import numpy
from PIL import Image
from fractions import Fraction
from datetime import datetime
import time
import argparse

class PiCamCapture:
    """Pi camera class """
    def __init__(self, resolution=(1648, 1232), framerate=Fraction(1, 5), iso=800, shutter_speed=5000000, duration=60, drc='off', fileprefix="./img", verbose=False):
        """Initialize pi camera for long duration captures"""
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera_iso = iso
        self.camera.shutter_speed = shutter_speed
        self.camera.drc_strength = drc
        self.camera.sensor_mode = 3
        self.verbose = verbose
        self.stopped = False
        self.frametime = time.time()
        self.newFrame = picamera.array.PiRGBArray(self.camera, size=resolution)
        if self.verbose:
            print("framerate: %3.3f" % framerate)
            print("shutter_speed: %d" % shutter_speed)
            print("stack_count: %d" % (duration/(shutter_speed/1000000)))
        self.stack = PiCamStack((duration/(shutter_speed/1000000)), fileprefix)
        time.sleep(10)

    def run(self):
        """Run pi camera capture sequence """
        if self.verbose:
            print("Starting capture")
        while True:
            try:
                self.camera.capture_sequence(self.gen_seq(), format="rgb", use_video_port=True)
            except KeyboardInterrupt:
                print("Keyboard break.")
                break
            except Exception as e:
                print(e)
                break
        self.stopped = True
        if self.verbose:
            print("Shutting down camera...")
        # set camera to normalish values and close
        self.camera.framerate = Fraction(10, 1)
        self.camera.shutter_speed = 100000
        time.sleep(3)
        self.camera.close()

    def gen_seq(self):
        """iterator function for capture_sequence"""
        while not self.stopped:
            yield self.newFrame
            # process the new frame here
            self.update()

    def update(self):
        """Process a new frame """
        if self.verbose:
            t0 = time.time()
            print("Frame time: %1.4f" % float(t0-self.frametime))
            self.frametime = t0
        self.newFrame.seek(0)
        self.stack.stack(self.newFrame.array)

    def stop(self):
        """Set flag to stop camera processing """
        self.stopped = True

class PiCamStack:
    """Image stacking class """
    def __init__(self, mult=6, fileprefix="./img"):
        """Constructor for image stacking class"""
        self.mult = mult
        self.fileprefix = fileprefix
        self.idx = -1
        self.stk = None
        self.filetime = datetime.now()

    def stack(self, new_frame):
        """Image stacking state machine """
        self.idx = self.idx + 1
        if self.idx == 0:
            # first time through
            self.filetime = datetime.now()
            self.stk = new_frame
        elif self.idx == 1:
            # write out current stack, initialize for next stack
            filename = self.fileprefix + "%s.jpg" % self.filetime.strftime("%Y%m%d%H%M%S")
            self.filetime = datetime.now()
            img = Image.fromarray(self.stk, mode="RGB")
            img.save(filename, "JPEG", quality=95, subsampling=0)
            print(filename)
            self.stk = new_frame
        elif self.idx < self.mult:
            # stack in progress
            self.stk = numpy.maximum(self.stk, new_frame)
        else:
            # last image for current stack
            self.stk = numpy.maximum(self.stk, new_frame)
            self.idx = 0

def main():
    """Main entry point, parse command line args and start camera"""
    print("Raspberry Pi camera long duration imager")
    parser = argparse.ArgumentParser(description="Raspberry Pi camera app for long duration exposures")
    parser.add_argument("-d", "--duration", help="Duration of image in seconds, default is 60", type=int, default=60)
    parser.add_argument("-e", "--exposure", help="Camera exposure time in milliseconds, default is 5000", type=int, default=5000)
    parser.add_argument("-f", "--fileprefix", help="Text added in front of filename, default is './img'", default="./img")
    parser.add_argument("-drc", help="Dynamic range compression, default is 'off'", choices=["off", "low", "medium", "high"], default="off")
    parser.set_defaults(verbose=False)
    parser.add_argument("-v", "--verbose", help="Print verbose details", action='store_true')
    args = parser.parse_args()

    if args.verbose:
        print(args)

    if args.duration < 10 or args.duration > 3600:
        print("Duration is outside of range [10-3600]")
        return 1

    if args.exposure < 500 or args.exposure > 10000:
        print("Exposure is outside of range [500-10000]")
        return 1

    if ((args.duration*1000) % args.exposure) != 0:
        print("Duration must be a multiple of exposure.")
        return 1

    print("Capture using %d" % args.exposure, "msec exposure, write stacked image every %d seconds" % args.duration)
    pcc = PiCamCapture(framerate=(1/(args.exposure/1000)), shutter_speed=(args.exposure*1000), duration=args.duration, drc=args.drc, fileprefix=args.fileprefix, verbose=args.verbose)
    pcc.run()

    print("\nExiting program.")

if __name__ == "__main__":
    main()

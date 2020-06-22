#!/usr/bin/env python
#-*- coding: UTF-8 -*-

# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO

#Steuert Pins an und setzt ausgewählten Pin zurück
GPIO.setmode(GPIO.BCM)
pin = 20
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, False)

#Methode zum Abgleichen
i = 0 #blinkt nur 3 mal
z = 0

#Array mit Fehlerliste. muss noch ergänzt werden 
errorlist = ["Nummer:01 Farbe:rot", "Nummer:02 Farbe:rot"]
correctlist = ["Nummer:11 Farbe:weiss", "Nummer:12 Farbe:weiss"]

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
    help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())
# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "w")
found = set()
# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)
# loop over the detected barcodes
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw
        # the bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 60, 60), 2)
        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 60, 60), 2)
        # Abfrage ob der inhalt teil der fehlerliste ist oder okay
        for e, c in zip(errorlist, correctlist):
            if e == barcodeData:
                warn = "Fehler"
                cv2.putText(frame, warn, (x - 50, y + 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 255), 2)
                while i <= 2:
                   i += 1
                   z += 1
                   print("LED blinkt ", z)
                   '''GPIO.output(pin, True)
                   time.sleep(1)
                   GPIO.output(pin, False)'''
            if c == barcodeData:
                right = "OK"
                cv2.putText(frame, right, (x - 25, y + 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (111, 255, 40), 2)
        # if the barcode text is currently not in our CSV file, write
        # the timestamp + barcode to disk and update the set
        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(),
                barcodeData))
            csv.flush()
            found.add(barcodeData)
# show the output frame
    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
 
    # if the `e` key was pressed, break from the loop
    if key == ord("e"):
        break
# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()


import cv2 as cv
import cv2.aruco as aruco
import numpy as np

import constants as cst
import projector
import camera

class CoreAR:
    def __init__(self, cam, proj):
        self.cam = cam
        self.proj = proj

    def calibrateCamera(self):
        self.proj.drawBlack()

        cornersCamera = []
        cornersBoard = []

        # Loop until we have the 4 corners
        while len(cornersCamera)<4:
            print(cornersCamera)
            # Detect markers in the camera image
            parmeters = aruco.DetectorParameters_create()
            dictionnary = aruco.Dictionary_get(aruco.DICT_6X6_250)
            markers, ids, rejectedImgPoints = aruco.detectMarkers(self.cam.getFrame(), dictionnary, parameters=parmeters)

            nbCornersDetected = 0

            # Get markers corresponding to corners
            ## TODO: loop on all markers
            ## for i in ...
            for i in range(len(markers)):
                if ids[i]==cst.N_MARKER_B1_TR:
                    cornersCamera.append(markers[i][0][0])
                    cornersBoard.append(cst.MARKER_B1_TR) 
                    nbCornersDetected += 1  

                if ids[i]==cst.N_MARKER_B1_TL:
                    ## TODO: add the corners to the lists
                    cornersCamera.append(markers[i][0][1])
                    cornersBoard.append(cst.MARKER_B1_TL)
                    nbCornersDetected += 1

                if ids[i]==cst.N_MARKER_B1_BL:
                    cornersCamera.append(markers[i][0][2])
                    cornersBoard.append(cst.MARKER_B1_BL)
                    nbCornersDetected += 1

                if ids[i]==cst.N_MARKER_B1_BR:
                    cornersCamera.append(markers[i][0][3])
                    cornersBoard.append(cst.MARKER_B1_BR)
                    nbCornersDetected += 1

            #If everything goes right, create the transformation matrix
            if nbCornersDetected==4:
                self.C2R, _ = cv.findHomography(np.array(cornersCamera), np.array(cornersBoard))

                self.cameraIsCalibrated = True

                #Display the corners
                resultFrame = self.cam.getFrame()
                aruco.drawDetectedMarkers(resultFrame, markers, borderColor=(0, 0, 255))
                cv.imshow(cst.WINDOW_MAIN, resultFrame)

                #Get the marker in real space
                cornersReal = cv.perspectiveTransform(np.array([cornersCamera]), self.C2R)

            else:
                # Clean the lists
                cornersCamera.clear()
                cornersBoard.clear()

    def calibrateProjector(self):
        pointsCamera = []
        pointsProjector = []

        # Loop until we have at least 8 points
        while len(pointsCamera)<8:
            pointsCamera.clear()
            pointsProjector.clear()

            # Draw markers on projector
            markersPts, markersId = self.proj.drawMarkers()

            # Wait a second
            cv.waitKey(1000)

            # Detect markers on camera
            parmeters = aruco.DetectorParameters_create()
            dictionnary = aruco.Dictionary_get(aruco.DICT_5X5_250)
            markers, ids, rejectedImgPoints = aruco.detectMarkers(self.cam.getFrame(), dictionnary, parameters=parmeters)

            # Get markers corresponding to the projected ones
            for i in range(len(markers)):
                if ids[i] in markersId:
                    pointsCamera.append(markers[i][0][0])
                    pointsProjector.append(markersPts[markersId.index(ids[i])])

        # Display the markers
        resultFrame = self.cam.getFrame()
        aruco.drawDetectedMarkers(resultFrame, markers, borderColor=(0, 0, 255))
        cv.imshow(cst.WINDOW_MAIN, resultFrame)

        # Create the transformation matrix
        pointsReal = cv.perspectiveTransform(np.array([pointsCamera]), self.C2R)[0]
        pointsProjector = np.array(pointsProjector)
        self.R2P, _ = cv.findHomography(pointsReal, pointsProjector)

    def findMove(self):
        # Get the current frame
        ## TODO
        ## frame = ...
        frame= self.cam.getFrame()

        # Convert to gray
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Find the difference between the reference frame and the current one
        ## TODO: using cv.absdiff
        ## diff = ...
        diff = cv.absdiff(gray, self.refFrame)
        
        # cv.imshow("Difference", diff)
        cv.imshow("Difference", diff)
        cv.waitKey(1)

        # Threshold
        ## TODO: using cv.threshold
        ## _, thresh = ...
        _, thresh = cv.threshold(diff, 50, 255, cv.THRESH_BINARY)

        # cv.imshow("Threshold", thresh)
        cv.imshow("Threshold", thresh)
        cv.waitKey(1)

        # Opening
        kernel = np.ones((5,5), np.uint8)
        opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)

        # Find new elements
        contours, hierarchy = cv.findContours(opening, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # Find the biggest contour
        biggest = None
        maxArea = 0
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area>maxArea:
                maxArea = area
                biggest = cnt
        
        # Draw the biggest contour
        if biggest is not None:
            cv.drawContours(frame, [biggest], -1, (0,255,0), 3)
            cv.imshow(cst.WINDOW_MAIN, frame)
            cv.waitKey(1)
        
            # Store the center
            M = cv.moments(biggest)
            cx = M['m10']/M['m00']
            cy = M['m01']/M['m00']

            # Get its position in real space
            center = []
            center.append([cx, cy])
            
            # On ajoute des crochets autour de 'center' pour avoir la bonne dimension
            # Et on utilise self.C2R !
            pos = cv.perspectiveTransform(np.array([center], dtype=np.float32), self.C2R)
            
            return pos[0][0]
                
    def storeRefFrame(self):
        self.refFrame = self.cam.getFrame()
        # Turn it gray
        self.refFrame = cv.cvtColor(self.refFrame, cv.COLOR_BGR2GRAY)
        #cv.imshow("Reference", self.refFrame)
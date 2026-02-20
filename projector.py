import constants as cst
import numpy as np

import cv2 as cv
import cv2.aruco as aruco

class Projector:
    def __init__(self):

        # Initialize the projector image and fill it with gray
        self.matDraw = np.zeros((cst.PROJ_HEIGHT, cst.PROJ_WIDTH, 3), np.uint8)
        self.matDraw[:] = cst.GRAY

        # Create the projector window and place it on the second screen
        cv.namedWindow(cst.WINDOW_PROJECTOR, cv.WINDOW_NORMAL)
        cv.moveWindow(cst.WINDOW_PROJECTOR,cst.FIRST_SCREEN_WIDTH,0)
        cv.setWindowProperty(cst.WINDOW_PROJECTOR, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

        # Display the projector image
        cv.imshow(cst.WINDOW_PROJECTOR, self.matDraw)
        cv.waitKey(1)
    
    def drawBlack(self):
        """
        ## TODO: Fill the image with black and display it
        self.matDraw[:] = cst.BLACK
        cv.imshow(cst.WINDOW_PROJECTOR, self.matDraw)
        cv.waitKey(1)
        """
        # On remplit tout en blanc pour garantir la zone de silence
        self.matDraw[:] = cst.WHITE
        
        # On récupère le dictionnaire d'Aruco
        arucoDict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        size = 150 # Taille du marqueur en pixels
        margin = 50 # <-- LA SOLUTION : On définit une marge en pixels
        
        # On génère les 4 images des marqueurs
        img_tl = cv.cvtColor(aruco.drawMarker(arucoDict, cst.N_MARKER_B1_TL, size, 1), cv.COLOR_GRAY2BGR)
        img_tr = cv.cvtColor(aruco.drawMarker(arucoDict, cst.N_MARKER_B1_TR, size, 1), cv.COLOR_GRAY2BGR)
        img_bl = cv.cvtColor(aruco.drawMarker(arucoDict, cst.N_MARKER_B1_BL, size, 1), cv.COLOR_GRAY2BGR)
        img_br = cv.cvtColor(aruco.drawMarker(arucoDict, cst.N_MARKER_B1_BR, size, 1), cv.COLOR_GRAY2BGR)
        
        h, w = self.matDraw.shape[:2]
        
        # Top-Left (décalé de 'margin' en X et en Y)
        self.matDraw[margin:margin+size, margin:margin+size] = img_tl
        
        # Top-Right
        self.matDraw[margin:margin+size, w-margin-size:w-margin] = img_tr
        
        # Bottom-Left
        self.matDraw[h-margin-size:h-margin, margin:margin+size] = img_bl
        
        # Bottom-Right
        self.matDraw[h-margin-size:h-margin, w-margin-size:w-margin] = img_br
        
        cv.imshow(cst.WINDOW_PROJECTOR, self.matDraw)
        cv.waitKey(1)

    def drawMarkers(self):
        newPts = []
        newIds = []

        # Initialize the projector image and fill it with white
        self.matDraw[:] = cst.WHITE

        # Get the first marker id
        nMarker = int(np.random.randint(1, 250))

        # Define parameters
        sizeMarker = int(self.matDraw.shape[0]/15.0)
        nMarkersX = int(self.matDraw.shape[1]/1.5/sizeMarker)
        nMarkersY = int(self.matDraw.shape[0]/1.5/sizeMarker)

        for i in range(nMarkersX):
            for j in range(nMarkersY):
                # Add the id to the list
                newIds.append(nMarker)

                # Compute the position of the marker and add the marker to the list
                corner = ((0.5+i*1.5)*sizeMarker, (0.5+j*1.5)*sizeMarker)
                newPts.append(corner)

                # Draw the marker
                arucoDict = aruco.Dictionary_get(aruco.DICT_5X5_250)
                img = aruco.drawMarker(arucoDict, nMarker, sizeMarker)

                # Add third channel
                img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

                # Draw the marker in the projector (! x and y are inverted)
                self.matDraw[int(corner[1]):int(corner[1]+sizeMarker), int(corner[0]):int(corner[0]+sizeMarker)] = img
                
                # Get the next marker id
                nMarker = (nMarker+1)%250
        
        # Display the image
        cv.imshow(cst.WINDOW_PROJECTOR, self.matDraw)
        cv.waitKey(1)

        return newPts, newIds
                
    def draw(self, mat):
        # Warp the image in the projector space and display it
        self.matDraw = cv.warpPerspective(mat, self.R2P, (cst.PROJ_WIDTH, cst.PROJ_HEIGHT))
        cv.imshow(cst.WINDOW_PROJECTOR, self.matDraw)
        cv.waitKey(1)

    def checkCalibration(self):
        # Create an image in real space
        mat = np.zeros(cst.BOARD_MAX_SIZE + (3,), np.uint8)

        # Fill the image with white
        mat[:] = cst.WHITE

        # Draw a rectangle around the board
        cv.rectangle(mat, (0,0), (cst.BOARD_MAX_SIZE[1], cst.BOARD_MAX_SIZE[0]), cst.BLACK, 2)

        # Draw a square for the playing area
        cv.rectangle(mat, cst.PLAYING_AREA_PT1, cst.PLAYING_AREA_PT2, cst.BLACK, 2)
        
        # Warp the image in the projector space and display it
        self.draw(mat)


# Test function in case this file is called directly
if __name__ == "__main__":
    # Create the projector
    proj = Projector()

    # Try to draw the black screen
    try:
        proj.drawBlack()
    except:
        print("Failed to draw black screen.")

    cv.waitKey(1000)

    # Try to draw the markers
    try:
        proj.drawMarkers()
    except:
        print("Failed to draw the markers.")
    
    cv.waitKey(1000)

    # Try to draw the calibration image
    try:
        proj.checkCalibration()
    except:
        print("Failed to draw the calibration image.")

    cv.waitKey(1000)
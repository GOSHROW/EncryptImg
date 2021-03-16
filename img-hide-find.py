import cv2
import numpy as np
import random

def hide(coverImgPath, toHideImgPath, outImgPath, outResTextPath):
    # Size of image at coverImgPath must surely be 
    # atleast thrice that of the image at toHideImagePath
    cover = cv2.imread(coverImgPath, 1)
    toHide = cv2.imread(toHideImgPath, 1)
    liCover = []
    for i in range(cover.shape[0]):
        for j in range(cover.shape[1]):
            liCover.append(cover[i][j])
    liToHide = []
    for i in range(toHide.shape[0]):
        for j in range(toHide.shape[1]):
            liToHide.append(toHide[i][j])
    k = 0
    for i in range(len(liToHide)):
        liCover[k] = liToHide[i]
        # k += random.randint(3, max(len(liCover) // len(liToHide), 2)) Use Henon Here for Definiteness
        k += max(len(liCover) // len(liToHide), 2) - 1
    hiddenImg = np.reshape(liCover, cover.shape)
    cv2.imwrite(outImgPath, hiddenImg)
    with open(outResTextPath, "w+") as hiddenFileSize:
        hiddenFileSize.write(str(toHide.shape[0]) + " " + str(toHide.shape[1]) + " " + str(toHide.shape[2]))

def reveal(inResTextPath, hiddenImgPath, revealedImgPath):
    originalShape = ()
    with open(inResTextPath, "r") as hiddenFileSize:
        originalShape = tuple(int(x) for x in hiddenFileSize.read().split())

    hidden = cv2.imread(hiddenImgPath, 1)
    liHidden= []
    for i in range(hidden.shape[0]):
        for j in range(hidden.shape[1]):
            liHidden.append(hidden[i][j])
    revealed = []
    k = 0
    for _ in range(originalShape[0] * originalShape[1]):
        revealed.append(liHidden[k])
        k += max(len(liHidden) // (originalShape[0] * originalShape[1]), 2) - 1
    revealedImg = np.reshape(revealed, originalShape)
    cv2.imwrite(revealedImgPath, revealedImg)

if __name__ == "__main__":
    hide("./cover.jpg", "./lena.jpg", "./hidden.png", "./hiddenFileSize")
    reveal("./hiddenFileSize", "./hidden.png", "./revealed.png")
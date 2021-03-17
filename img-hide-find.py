import cv2
import numpy as np
import json

def randomLiHide(keysTextPath, toHideImgPath, coverImgPath):
    ao, c, l = 0, 0, 0
    with open(keysTextPath) as jsonKeys:
        akgm = json.load(jsonKeys)["akgm"]
        ao, c = float(akgm[0]) / (int(akgm[0]) + 1), (1 + str(akgm[1]).count('0'))
    imgShape = cv2.imread(toHideImgPath, 0).shape
    l = imgShape[0] * imgShape[1]
    coverShape = cv2.imread(coverImgPath, 0).shape
    coverLen = coverShape[0] * coverShape[1]
    maxDistance = coverLen // l
    m = maxDistance

    randomLi = []
    for iters in range(l):
        ao = c * ao * (1 - ao)
        sumDigits = sum(int(i) if i in '0123456789' else 0 for i in str(ao)) % m
        randomLi.append(1 + sumDigits)
    # from collections import Counter
    # print(Counter(randomLi), len(randomLi))
    return randomLi

def randomLiReveal(keysTextPath, resTextPath, hiddenImagePath):
    ao, c, l = 0, 0, 0
    with open(keysTextPath) as jsonKeys:
        akgm = json.load(jsonKeys)["akgm"]
        ao, c = float(akgm[0]) / (int(akgm[0]) + 1), (1 + str(akgm[1]).count('0'))
    with open(resTextPath) as resolution:
        imgShape = [int(x) for x in resolution.read().split()]
        l = imgShape[0] * imgShape[1]
    coverShape = cv2.imread(hiddenImagePath, 0).shape
    coverLen = coverShape[0] * coverShape[1]
    maxDistance = coverLen // l
    m = maxDistance

    randomLi = []
    for iters in range(l):
        ao = c * ao * (1 - ao)
        sumDigits = sum(int(i) if i in '0123456789' else 0 for i in str(ao)) % m
        randomLi.append(1 + sumDigits)
    # from collections import Counter
    # print(Counter(randomLi), len(randomLi))
    return randomLi

def hide(coverImgPath, toHideImgPath, outImgPath, outResTextPath, keysTextPath):
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

    distanceLi = randomLiHide(keysTextPath, toHideImgPath, coverImgPath)
    for i in range(len(liToHide)):
        liCover[k] = liToHide[i]
        k += distanceLi[i]
    hiddenImg = np.reshape(liCover, cover.shape)
    cv2.imwrite(outImgPath, hiddenImg)
    with open(outResTextPath, "w+") as hiddenFileSize:
        hiddenFileSize.write(str(toHide.shape[0]) + " " + str(toHide.shape[1]) + " " + str(toHide.shape[2]))

def reveal(inResTextPath, hiddenImgPath, revealedImgPath, keysTextPath):
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

    distanceLi = randomLiReveal(keysTextPath, inResTextPath, hiddenImgPath)
    # print(len(distanceLi), originalShape[0] * originalShape[1])
    for i in range(originalShape[0] * originalShape[1]):
        revealed.append(liHidden[k])
        k += distanceLi[i]
    revealedImg = np.reshape(revealed, originalShape)
    cv2.imwrite(revealedImgPath, revealedImg)

if __name__ == "__main__":
    hide("./cover.jpg", "./encrypted.png", "./hidden.png", "./hiddenFileSize", "./keys.txt")
    reveal("./hiddenFileSize", "./hidden.png", "./revealed.png", "./keys.txt")
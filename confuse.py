# def confusez3(img):
#     n, m, _ = img.shape
#     i = 0
#     visited = [[False for x in range(m)] for y in range(n)]
#     visited[0][0] = True
#     resImg = [img[0][0]]
#     x, y = 0, 0
#     while i < ((m * n) - 1):
#         i += 1
#         if (x-1) in range(0, m) and (y+1) in range(0, n) and visited[y+1][x-1] == False:
#             x = x - 1
#             y = y + 1
#         elif (x+1) in range(0, m) and (y-1) in range(0, n) and visited[y-1][x+1] == False:
#             x = x + 1
#             y = y - 1
#         elif x == 0 or x == m - 1:
#             y = y + 1
#         elif y == 0 or y == n - 1:
#             x = x + 1
#         visited[y][x] = True
#         resImg.append(img[y][x])
#     return resImg

# import cv2
# import numpy as np
# img = cv2.imread("./confused4.png", 1)
# imageShape = (img.shape[0], img.shape[1], 1)
# matBase = np.reshape(np.array(list(range(0, imageShape[0] * imageShape[1]))), imageShape)
# confusedMatBase = confusez3(matBase)
# confusedBaseDict = {}
# for i, e in enumerate(confusedMatBase):
#     confusedBaseDict[tuple(e[:])] = i 
# print(confusedBaseDict)

# matToCheck = cv2.imread("./confused4.png", 1)
# matToCheck = confusez3(matToCheck)
# reverseScan = []
# for i in range(imageShape[0] * imageShape[1]):
#     print(i)
#     reverseScan.append(matToCheck[confusedBaseDict[tuple(np.array([i])[:])]])
# print(reverseScan)
# cv2.imwrite("confuse1.png", reverseScan)
# # print(confusez3(mat).index([10]))

def confusez3(img):
    n, m, _ = img.shape
    i = 0
    visited = [[False for x in range(m)] for y in range(n)]
    visited[0][0] = True
    resImg = [img[0][0]]
    x, y = 0, 0
    while i < ((m * n) - 1):
        i += 1
        if (x-1) in range(0, m) and (y+1) in range(0, n) and visited[y+1][x-1] == False:
            x = x - 1
            y = y + 1
        elif (x+1) in range(0, m) and (y-1) in range(0, n) and visited[y-1][x+1] == False:
            x = x + 1
            y = y - 1
        elif x == 0 or x == m - 1:
            y = y + 1
        elif y == 0 or y == n - 1:
            x = x + 1
        visited[y][x] = True
        resImg.append(img[y][x])
    return resImg

def rConfusez3(img):
    imageShape = (img.shape[0], img.shape[1], 1)
    matBase = np.reshape(np.array(list(range(0, imageShape[0] * imageShape[1]))), imageShape)
    confusedMatBase = confusez3(matBase) 
    confusedMat = confusez3(img)
    confusedBaseDict = {}
    for i, e in enumerate(confusedMatBase):
        confusedBaseDict[tuple(e[:])] = i

    matToCheck = np.reshape(img, (img.shape[0] * img.shape[1], 3))
    print(matToCheck.shape)
    reverseScan = []
    for i in range(imageShape[0] * imageShape[1]):
        reverseScan.append(matToCheck[confusedBaseDict[tuple(np.array([i])[:])]])
    with open("reverseScan", "a+") as rScan:
        rScan.write(str(reverseScan))
    return np.array(reverseScan).reshape(img.shape)

import cv2
import numpy as np

rconfused = rConfusez3(cv2.imread("./permuted.png", 1))
cv2.imwrite("reversePermuted.png", rconfused)
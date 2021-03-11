def confusez3(img):
    n, m, _ = img.shape
    i = 0
    visited = [[False for x in range(m)] for y in range(n)]
    visited[0][0] = True
    # print(visited)
    resImg = [img[0][0]]
    x, y = 0, 0
    while i < ((m * n) - 1):
        i += 1
        # print(i, y, x, img[y][x])
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
    return np.reshape(resImg, img.shape)

import cv2
import numpy as np

img = cv2.imread("./lena.jpg")
# print(img.shape, np.transpose(img, (1, 0, 2)).shape)
# img = np.transpose(img, (1, 0, 2))
img = cv2.flip(np.transpose(img, (1, 0, 2)), 1)
newImg = confusez3(img)
cv2.imwrite("./confused2lena.jpg", newImg) # np.transpose(newImg, (1, 0, 2))
import cv2
import json
import numpy as np
import copy

class Decrypt:

    def __init__(self, encryptedImagePath, keysPath, outPath):
        self.image = cv2.imread(encryptedImagePath, 1)
        with open(keysPath) as jsonKeys:
            self.keys = json.load(jsonKeys)
        self.outPath = outPath

    def henon2DOut(self, xIn, yIn, outLen, b = 1.4, c = 0.3):
        ret = []
        for iteration in range(outLen):
            xNew = 1 - b * xIn * xIn + yIn
            yNew = c * yIn
            ret.append([xNew, yNew])
            xIn, yIn = xNew, yNew
        return tuple(zip(*ret))
    
    def getKeyBits(self, henonMap2d):
        Y, Z = henonMap2d
        Y = np.floor(np.array(Y) * 10**14) 
        Z = np.floor(np.array(Z) * 10**14) 
        Y = list((255*(Y - np.min(Y))/np.ptp(Y)).astype(int))
        Z = list((255*(Z - np.min(Z))/np.ptp(Z)).astype(int))
        keySeq = [Y[i] ^ Z[i] for i in range(len(Y))]
        keyBits = []
        for keyQ in keySeq:
            toAppend = str(bin(keyQ)[2:]).zfill(8)[::-1]
            keyBits.append([int(i) for i in toAppend])
        return keyBits
    
    def diffusionKeys(self, l):
        akgmInitial = self.keys["akgm"]
        keyBits = self.getKeyBits(self.henon2DOut(float(akgmInitial[0]), float(akgmInitial[1]), l))
        return keyBits
    
    def getCipherBits(self, image):
        image = image.ravel()
        l = len(image)
        cipherbits = []
        # lenset = set()
        for c in range(l):
            toAppend = str(bin(image[c])[2:]).zfill(8)[::-1]
            cipherbits.append([int(a) for a in toAppend])
            # lenset.add(len(toAppend))
        # print(lenset)
        return cipherbits

    def getPermute(self, keybits, cipherBits):
        l = len(cipherBits)
        keyBits = copy.deepcopy(keybits)
        # Padding 0s for 1 indexing
        cipherBits.insert(0, [0 for _ in range(8)])
        keyBits.insert(0, [0 for _ in range(8)])
        # print(np.array(perBits).shape, "  ", np.array(keyBits).shape)
        for i in range(l + 1):
            cipherBits[i] = [0] + cipherBits[i]
            keyBits[i] = [0] + keyBits[i]
        # print(np.array(keyBits).shape)
        b1 = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("ciphertextDEcrypt", "a+") as cipherD:
        #     cipherD.write(str(cipherBits))
        # with open("keyDEcrypt", "a+") as cipherD:
        #     cipherD.write(str(keyBits))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d <= 4:
                    b1[q][d] = cipherBits[q][d + 4] ^ keyBits[q][d]
                else:
                    b1[q][d] = cipherBits[q][d - 4] ^ keyBits[q][d]
        b2 = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("step1backD", "a+") as ciphertxt:
        #     ciphertxt.write(str(b1))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d in [1, 2, 5, 6]:
                    b2[q][d] = b1[q][d + 2] ^ keyBits[q][d]
                else:
                    b2[q][d] = b1[q][d - 2] ^ keyBits[q][d]
        permute = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("step2backD", "a+") as ciphertxt:
        #     ciphertxt.write(str(b2))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d % 2 != 0:
                    permute[q][d] = b2[q][d + 1] ^ keyBits[q][d] # TODO: Check Sign
                else:
                    permute[q][d] = b2[q][d - 1] ^ keyBits[q][d]
        # with open("step3backD", "a+") as ciphertxt:
        #     ciphertxt.write(str(permute))
        permute = permute[1:]
        for i in range(l):
            permute[i] = permute[i][1:]
        for pixel in range(len(permute)):
            asStr = ''.join([str(i) for i in permute[pixel]])[::-1]
            permute[pixel] = int(asStr, 2)
        permute = np.reshape(permute, (self.image.shape[0], self.image.shape[1]))
        return permute
    
    def reverseDiffusion3(self):
        W, X, planes = self.image.shape
        b, g, r = np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8)
        b[:,:] = self.image[:,:,0]
        g[:,:] = self.image[:,:,1]
        r[:,:] = self.image[:,:,2]
        # cv2.imwrite("./bIN.png", b)
        # cv2.imwrite("./gIN.png", g)
        # cv2.imwrite("./rIN.png", r)
        Keys = self.diffusionKeys(len(b.ravel()))
        # with open("keybitsDecrypt", "w+") as kbdf:
        #     kbdf.write(str(Keys))
        bCipher = self.getCipherBits(b)
        gCipher = self.getCipherBits(g)
        rCipher = self.getCipherBits(r)
        # with open("gcipherdecrypt", "w+") as gcipherd:
        #     gcipherd.write(str(gCipher))
        # print(np.array(bCipher).shape, np.array(Keys).shape)
        bPermute = self.getPermute(Keys, bCipher)
        gPermute = self.getPermute(Keys, gCipher)
        rPermute = self.getPermute(Keys, rCipher)
        return cv2.merge((bPermute, gPermute, rPermute))

    def permuteHenon(self, l = 4, b = 1.4, c = 0.3):
        xIn, yIn = float(self.keys["okgm"][0]), float(self.keys["okgm"][1])
        ret = []
        for iteration in range(l):
            xNew = 1 - b * xIn * xIn + yIn
            yNew = c * yIn
            ret.append([xNew, yNew])
            xIn, yIn = xNew, yNew
        henonMap1d = list(zip(*ret))[0]
        return list((255*(henonMap1d - np.min(henonMap1d))/np.ptp(henonMap1d)).astype(int))

    def confusez3(self, img):
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

    def rConfuse(self, img, zigzagDirection):
        imageShape = (img.shape[0], img.shape[1], 1)
        matBase = np.reshape(np.array(list(range(0, imageShape[0] * imageShape[1]))), imageShape)
        # confusedMatBase = self.confusez3(np.reshape(cv2.flip(matBase, 0), imageShape))
        # print(matBase.shape, len(confusedMatBase))
        
        if zigzagDirection == "z1":
            confusedMatBase = self.confusez3(np.transpose(matBase, (1, 0, 2)))
        elif zigzagDirection == "z2":
            confusedMatBase = self.confusez3(np.reshape(cv2.flip(np.transpose(matBase, (1, 0, 2)), 1), imageShape))
        elif zigzagDirection == "z3":
            confusedMatBase = self.confusez3(matBase)
        elif zigzagDirection == "z4":
            confusedMatBase = self.confusez3(np.reshape(cv2.flip(matBase, 0), imageShape))
        
        confusedBaseDict = {}
        for i, e in enumerate(confusedMatBase):
            confusedBaseDict[tuple(e[:])] = i

        matToCheck = np.reshape(img, (imageShape[0] * imageShape[1], 3))
        reverseScan = []
        for i in range(imageShape[0] * imageShape[1]):
            reverseScan.append(matToCheck[confusedBaseDict[tuple(np.array([i])[:])]])
        # with open("reverseScan", "a+") as rScan:
        #     rScan.write(str(reverseScan))
        return np.array(reverseScan).reshape((imageShape[0], imageShape[1], 3))

    def reverseConfusion(self, image, henonConfusion):
        zigzagDirections = []
        for i in henonConfusion[::-1]:
            if(0 <= i <= 63):
                zigzagDirections.append("z1")
            elif(64 <= i <= 127):
                zigzagDirections.append("z2")
            elif(128 <= i <= 191):
                zigzagDirections.append("z3")
            elif(192 <= i <= 255):
                zigzagDirections.append("z4")

        for idx, i in enumerate(zigzagDirections):
            image = self.rConfuse(image, i)
            # cv2.imwrite("./confusedD" + str(idx + 1) + ".png", image)
        return image

    def main(self):
        permutedImage = self.reverseDiffusion3()
        # cv2.imwrite("./permuted.png", permutedImage)
        permuteHenonMap = self.permuteHenon()
        decrypted = self.reverseConfusion(permutedImage, permuteHenonMap)
        cv2.imwrite("./decrypted.png", decrypted)

if __name__ == "__main__":
    decrypt = Decrypt("./encrypted.png", "./keys.txt", "./decrypted.png")
    decrypt.main()
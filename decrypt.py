import cv2
import json
import numpy as np

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
    
    def diffusionKeys(self, image):
        l = len(image.ravel())
        akgmInitial = self.keys["akgm"]
        keyBits = self.getKeyBits(self.henon2DOut(float(akgmInitial[0]), float(akgmInitial[1]), l))
        return keyBits
    
    def getCipherBits(self, image):
        image = image.ravel()
        l = len(image)
        cipherbits = []
        lenset = set()
        for c in range(l):
            toAppend = str(bin(image[c])[2:]).zfill(8)[::-1]
            cipherbits.append([int(a) for a in toAppend])
            lenset.add(len(toAppend))
        return cipherbits

    def getPermute(self, keyBits, cipherBits):
        l = len(cipherBits)
        # Padding 0s for 1 indexing
        cipherBits.insert(0, [0 for _ in range(8)])
        keyBits.insert(0, [0 for _ in range(8)])
        # print(np.array(perBits).shape, "  ", np.array(keyBits).shape)
        for i in range(l + 1):
            cipherBits[i] = [0] + cipherBits[i]
            keyBits[i] = [0] + keyBits[i]
        b1 = [[0 for i in range(9)] for j in range(l + 1)]
        for q in range(1, l+1):
            for d in range(1, 9):
                if d <= 4:
                    b1[q][d] = cipherBits[q][d + 4] ^ keyBits[q][d + 4]
                else:
                    b1[q][d] = cipherBits[q][d - 4] ^ keyBits[q][d - 4]
        b2 = [[0 for i in range(9)] for j in range(l + 1)]
        for q in range(1, l+1):
            for d in range(1, 9):
                if d in [1, 2, 5, 6]:
                    b2[q][d] = b1[q][d + 2] ^ keyBits[q][d + 2]
                else:
                    b2[q][d] = b1[q][d - 2] ^ keyBits[q][d - 2]
        permute = [[0 for i in range(9)] for j in range(l + 1)]
        for q in range(1, l+1):
            for d in range(1, 9):
                if d % 2 != 0:
                    permute[q][d] = b2[q][d + 1] ^ keyBits[q][d + 1] # TODO: Check Sign
                else:
                    permute[q][d] = b2[q][d - 1] ^ keyBits[q][d - 1]
        permute = permute[1:]
        for i in range(l):
            permute[i] = permute[i][1:]
        for pixel in range(len(permute)):
            asStr = ''.join([str(i) for i in permute[pixel]])[::-1]
            permute[pixel] = int(asStr, 2)
        permute = np.reshape(permute, (self.image.shape[0], self.image.shape[1]))
        return permute
    
    def unify3(self):
        W, X, planes = self.image.shape
        b, g, r = np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8)
        b[:,:] = self.image[:,:,0]
        g[:,:] = self.image[:,:,1]
        r[:,:] = self.image[:,:,2]
        bKeys = self.diffusionKeys(b)
        gKeys = self.diffusionKeys(g)
        rKeys = self.diffusionKeys(r)
        bCipher = self.getCipherBits(b)
        gCipher = self.getCipherBits(g)
        rCipher = self.getCipherBits(r)
        # print(np.array(bCipher).shape, np.array(bKeys).shape)
        bPermute = self.getPermute(bKeys, bCipher)
        gPermute = self.getPermute(gKeys, gCipher)
        rPermute = self.getPermute(rKeys, rCipher)
        return cv2.merge((rPermute, gPermute, bPermute))

    def main(self):
        permutedImage = self.unify3()
        cv2.imwrite("./permuted.jpg", permutedImage)

decrypt = Decrypt("./encrypted.jpg", "./keys.txt", "./decrypted.jpg")
decrypt.main()
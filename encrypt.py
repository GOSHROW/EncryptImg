from decimal import Decimal
import numpy as np
import random
import cv2
import json

class Encrypt:
    def __init__(self, imagePath, outImgPath, outKeysPath):
        self.image = cv2.imread(imagePath, 1)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.outImgPath = outImgPath
        self.outKeysPath = outKeysPath

    def henon1DOut(self, xIn, yIn, outLen, b = 1.4, c = 0.3):
        ret = []
        for iteration in range(outLen):
            xNew = 1 - b * xIn * xIn + yIn
            yNew = c * yIn
            ret.append([xNew, yNew])
            xIn, yIn = xNew, yNew
        return list(zip(*ret))[0] # to get only 1d results

    def scaleHenonOut(self, henonMap1d):
        return list((255*(henonMap1d - np.min(henonMap1d))/np.ptp(henonMap1d)).astype(int))

    def AKGM(self):
        W, X, planes = self.image.shape
        b, g, r = np.zeros((W, X, planes),np.uint8), np.zeros((W, X, planes),np.uint8), np.zeros((W, X, planes),np.uint8)
        b[:,:,2] = self.image[:,:,2]
        g[:,:,1] = self.image[:,:,1]
        r[:,:,0] = self.image[:,:,0]
        # cv2.imwrite("./rout.jpg", b)
        # cv2.imwrite("./gout.jpg", g)
        # cv2.imwrite("./bout.jpg", r)
        rHist = np.histogram(r.ravel(), bins = list(range(0, 256)))
        gHist = np.histogram(g.ravel(), bins = list(range(0, 256)))
        bHist = np.histogram(b.ravel(), bins = list(range(0, 256)))
        rgHist = [abs(rHist[0][i] - gHist[0][i]) for i in range(len(rHist[0]))]
        rgHist = np.array(rgHist)
        gbHist = [abs(bHist[0][i] - gHist[0][i]) for i in range(len(rHist[0]))]
        gbHist = np.array(gbHist)
        brHist = [abs(bHist[0][i] - rHist[0][i]) for i in range(len(rHist[0]))]
        brHist = np.array(brHist)
        rg_gb_distance = np.sqrt(sum((rgHist[i] - gbHist[i]) ** 2 for i in range(len(rgHist))))
        gb_br_distance = np.sqrt(sum((brHist[i] - gbHist[i]) ** 2 for i in range(len(rgHist))))
        retY = Decimal(str(rg_gb_distance)) % 1
        retZ = Decimal(str(gb_br_distance)) % 1
        return (float(retY), float(retZ))

    def OKGM(self):
        W, X, _ = self.image.shape
        def helper():
            randomNoDecimal = random.randint(1, W * X )
            randomNoBinary = bin(randomNoDecimal)[2:]
            twoPowers = 2
            fractionalDecimal = 0
            for i in range(len(randomNoBinary)):         
                fractionalDecimal += ((ord(randomNoBinary[i]) - ord('0')) / twoPowers); 
                twoPowers *= 2.0
            return fractionalDecimal
        retY = helper()
        retZ = helper()
        return (retY, retZ)

    def out(self, okgmInitial, akgmInitial):
        keys = {
            "okgm": okgmInitial,
            "akgm": akgmInitial
        }
        with open(self.outKeysPath, 'w+') as outfile:
            json.dump(keys, outfile)
        # IF the outPath is using lossy compression, rather send out the text as is. 
        # with open('encrypteeFinal', 'w+') as encryptText:
        #     encryptText.write(str(self.image))
        cv2.imwrite(self.outImgPath, self.image)

    def confusez3(self, img):
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

    def zigzagConfuse(self, henonConfusion):
        zigzagDirections = []
        for i in henonConfusion:
            if(0 <= i <= 63):
                zigzagDirections.append("z1")
            elif(64 <= i <= 127):
                zigzagDirections.append("z2")
            elif(128 <= i <= 191):
                zigzagDirections.append("z3")
            elif(192 <= i <= 255):
                zigzagDirections.append("z4")
        image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

        for idx, i in enumerate(zigzagDirections):
            if i == "z1":
                image = self.confusez3(np.transpose(image, (1, 0, 2)))
            elif i == "z2":
                image = self.confusez3(cv2.flip(np.transpose(image, (1, 0, 2)), 1))
            elif i == "z3":
                image = self.confusez3(image)
            elif i == "z4":
                image = self.confusez3(cv2.flip(image, 0))
            # cv2.imwrite("./confused" + str(idx + 1) + ".png", image)
        return image
    
    def henon2DOut(self, xIn, yIn, outLen, b = 1.4, c = 0.3):
        ret = []
        for iteration in range(outLen):
            xNew = 1 - b * xIn * xIn + yIn
            yNew = c * yIn
            ret.append([xNew, yNew])
            xIn, yIn = xNew, yNew
        return tuple(zip(*ret))

    def BNT3Layers(self, perBits, keyBits):
        l = len(perBits)
        # Padding 0s for 1 indexing
        perBits.insert(0, [0 for _ in range(8)])
        keyBits.insert(0, [0 for _ in range(8)])
        # print(np.array(perBits).shape, "  ", np.array(keyBits).shape)
        for i in range(l + 1):
            perBits[i] = [0] + perBits[i]
            keyBits[i] = [0] + keyBits[i]
        # print(np.array(perBits).shape, "  ", np.array(keyBits).shape)
        c1 = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("step3back", "a+") as ciphertxt:
        #     ciphertxt.write(str(perBits))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d % 2 != 0:
                    c1[q][d] = perBits[q][d + 1] ^ keyBits[q][d + 1]
                else:
                    c1[q][d] = perBits[q][d - 1] ^ keyBits[q][d - 1]
        c2 = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("step2back", "a+") as ciphertxt:
        #     ciphertxt.write(str(c1))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d in [1, 2, 5, 6]:
                    c2[q][d] = c1[q][d + 2] ^ keyBits[q][d + 2]
                else:
                    c2[q][d] = c1[q][d - 2] ^ keyBits[q][d - 2]
        cipher = [[0 for i in range(9)] for j in range(l + 1)]
        # with open("step1back", "a+") as ciphertxt:
        #     ciphertxt.write(str(c2))
        for q in range(1, l+1):
            for d in range(1, 9):
                if d <= 4:
                    cipher[q][d] = c2[q][d + 4] ^ keyBits[q][d + 4]
                else:
                    cipher[q][d] = c2[q][d - 4] ^ keyBits[q][d - 4]
        # with open("ciphertxtEncrypted", "a+") as ciphertxt:
        #     ciphertxt.write(str(cipher))
        # with open("keyEncrypt", "a+") as ciphertxt:
        #     ciphertxt.write(str(keyBits))
        cipher = cipher[1:]
        for i in range(l):
            cipher[i] = cipher[i][1:]
        return cipher

    def diffusion(self, image, akgmInitial):
        perSequence = image.ravel()
        l = len(perSequence)
        perBits = []
        for perQ in perSequence:
            toAppend = str(bin(perQ)[2:]).zfill(8)[::-1]
            perBits.append([int(i) for i in toAppend])
        keyBits = self.getKeyBits(self.henon2DOut(akgmInitial[0], akgmInitial[1], l))
        cipherbits = self.BNT3Layers(perBits, keyBits)
        encryptedImage = [0 for _ in range(len(cipherbits))]
        for pixel in range(len(cipherbits)):
            encryptedImage[pixel] = int(''.join([str(i) for i in cipherbits[pixel]])[::-1], 2)
        encryptedImage = np.reshape(encryptedImage, image.shape)
        return encryptedImage

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

    def channelMerge(self, b, g, r):
        shape = b.shape
        retImg = [[[0, 0, 0] for i in range(shape[1])] for j in range(shape[0])]
        for i in range(shape[0]):
            for j in range(shape[1]):
                retImg[i][j] = [b[i][j], g[i][j], r[i][j]]
        return np.array(retImg)

    def diffusion3(self, image, akgmInitial):
        W, X, planes = image.shape
        b, g, r = np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8), np.zeros((W, X),np.uint8)
        b[:,:] = image[:,:,0]
        g[:,:] = image[:,:,1]
        r[:,:] = image[:,:,2]
        # print(b.shape, g.shape, r.shape)
        bEncrypted = self.diffusion(b, akgmInitial)
        gEncrypted = self.diffusion(g, akgmInitial)
        rEncrypted = self.diffusion(r, akgmInitial)
        # cv2.imwrite("./bout.png", bEncrypted)
        # cv2.imwrite("./gout.png", gEncrypted)
        # cv2.imwrite("./rout.png", rEncrypted)
        final = self.channelMerge(bEncrypted, gEncrypted, rEncrypted)
        return final
        
    def main(self):
        akgmInitial = self.AKGM()
        okgmInitial = self.OKGM()
        henonConfusion = self.scaleHenonOut(self.henon1DOut(okgmInitial[0], okgmInitial[1], 4))
        confusedImage = self.zigzagConfuse(henonConfusion)
        self.image = self.diffusion3(confusedImage, akgmInitial)
        self.out(okgmInitial, akgmInitial)

if __name__ == "__main__":
    encrypted = Encrypt("./original.jpg", "./encrypted.png", "./keys.txt")
    encrypted.main()
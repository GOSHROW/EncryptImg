from encrypt import Encrypt
from naiveRandomizedSequenceImgHideReveal import hide, reveal
from decrypt import Decrypt
import cv2
import datetime

class Main:
    def encrypt(self, imagePath, outImgPath, outKeysPath):
        Encrypt(imagePath, outImgPath, outKeysPath).main()

    def hideImg(self, coverImgPath, toHideImgPath, outImgPath,
        outResTextPath, keysTextPath):
        hide(coverImgPath, toHideImgPath, outImgPath,
             outResTextPath, keysTextPath)

    def revealImg(self, inResTextPath, hiddenImgPath, revealedImgPath,
        keysTextPath):
        reveal(inResTextPath, hiddenImgPath, revealedImgPath, keysTextPath)
    
    def decrypt(self, encryptedImagePath, keysPath, outImgPath):
        Decrypt(encryptedImagePath, keysPath, outImgPath).main()
    
    def compareImg(self, originalImgPath, finalImgPath):
        failMsg = "Lost information during the Encryption-Decryption process"
        assert (cv2.imread(originalImgPath) == cv2.imread(finalImgPath)).all(), failMsg
        
if __name__ == "__main__":
    ob = Main()
    print("Encrypting . . .")
    curTime = datetime.datetime.now()
    ob.encrypt("./original.jpg", "./encrypted.png", "./keys.txt")
    print("Finished in", datetime.datetime.now() - curTime)
    curTime = datetime.datetime.now()
    print("Hiding . . .")
    ob.hideImg("./cover.jpg", "./encrypted.png", "./hidden.png",
               "./hiddenFileSize.txt", "./keys.txt")
    print("Finished in", datetime.datetime.now() - curTime)
    curTime = datetime.datetime.now()
    print("Revealing . . .")
    ob.revealImg("./hiddenFileSize.txt", "./hidden.png",
                 "./revealed.png", "./keys.txt")
    print("Finished in", datetime.datetime.now() - curTime)
    curTime = datetime.datetime.now()
    print("Decrypting . . .")
    ob.decrypt("./revealed.png", "./keys.txt", "./decrypted.png")
    print("Finished in", datetime.datetime.now() - curTime)
    curTime = datetime.datetime.now()
    ob.compareImg("./original.jpg", "./decrypted.png")

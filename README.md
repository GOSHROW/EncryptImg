# Image Encryption and Steganography

This codebase implements a pretty fast and secure image encryption method with a further naive stagnorgarphy of the image. There are two sets of keys developed independently, such that each of them is capable of yielding a Henon Map of suitable length.

The first Henon Map is applied onto a 4-way ZigZag Scan of the Image. After properly permuting the base image, it is diffused through 3-layer internal permutation. Finally, the same can optionally be masked by an image of any larger dimensions so as to avoid being spotted as an encrypted image.

Thereafter, each of these steps is faithfully reversed to restore the original image.

The implementation partly uses https://doi.org/10.1007/s11042-020-09462-9 for the Encryption methods.

## Set-Up

- Python3.x
- opencv-python

For the specific installation,

```
git clone https://github.com/GOSHROW/EncryptImg
cd EncryptImage
pip3 install -r requirements.txt
```

Thereby, we need 2 accessible images for testing:

1. Image to be encrypted and hidden.
1. Image to be used for hiding, this must be atleast of 100% size of the other image, preferably much larger (~10x).

## Usage

To test the working,

```
python3 main.py
```

Moreover, the class _Main_ in `main.py` file can also be used as an importable module. Available interfaces are:

- **encrypt**(imagePath, outImgPath, outKeysPath)

  - imagePath : filepath to the image to be encrypted
  - outImgPath : filepath onto which the encrypted image is to be written
  - outKeysPath : filepath onto which the encryption keys are to be written, assumed to be safely transported to the decryptor

- **hideImg**(coverImgPath, toHideImgPath, outImgPath, outResTextPath, keysTextPath)

  - coverImgPath : filepath to the image to be used as a cover
  - toHideImgPath : filepath to the image to be hidden inside cover image
  - outImgPath : filepath onto which the hidden image is to be written
  - outResTextPath : filepath onto which shape of the encrypted image is to be written, assumed to be safely transported to the image-revealing component
  - keysTextPath : filepath onto which the keys were written in _encrypt(...)_

- **revealImg**(inResTextPath, hiddenImgPath, revealedImgPath, keysTextPath)

  - inResTextPath : filepath onto which _hideImg(...)_ wrote the encrypted image's resolution
  - hiddenImgPath : filepath for the image written out by _hideImg(...)_
  - revealedImgPath : filepath onto which the revealed image is to be written
  - keysTextPath : filepath onto which the keys were written in _encrypt(...)_

- **decrypt**(encryptedImagePath, keysPath, outImgPath)

  - encryptedImagePath : filepath to the image written out by either _encrypt(...)_ or _revealImg(...)_
  - keysPath : filepath onto which the keys were written in _encrypt(...)_
  - outImgPath : filepath onto which the decrypted image is to be written

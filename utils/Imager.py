#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pillow_avif
from pillow_heif import register_heif_opener


class Imager:


    def __init__(self):
        """Initialize."""

        from ..utils import loggingGet, getPaths, jsonLoad
        self.logger = loggingGet(str(self.__class__.__name__).lower())

        self.paths = getPaths()

        self.ioSettings = jsonLoad(self.paths['io_settings']['path'], self.logger)

        self.orientation = 'landscape'

        self._generatePalette()


        return
    

    def getImageInfo(self, imagePath):
        """Get image stats from path."""

        imageInfo = {}

        if os.path.exists(imagePath):

            rawImage = Image.open(imagePath).convert('RGB')
            rawImage = ImageOps.exif_transpose(rawImage)

            imageInfo['size'] = rawImage.size


        return imageInfo
    def getQuantizedBuffer(self, imagePath):
        """Format image for e-paper from path."""

        quantizedBufferedImage = []

        if os.path.exists(imagePath):

            quantizedBufferedImage = self._profiledImageFromPath(imagePath, self._displaySize())

            return self._bufferImage(quantizedBufferedImage)


        return quantizedBufferedImage
    def generateThumbnails(self, imagePath):
        """Generate thumbnails."""

        thumbnailPathsAndSizes = [
            {
                'file': '%(base)s_%(w)dx%(h)d.jpg' % {
                    'base': str(imagePath.rsplit(os.sep, 1)[-1]).rsplit('.', 1)[0],
                    'w': thumbnailSize['width'],
                    'h': thumbnailSize['height']
                },
                'path': os.path.join(
                    imagePath.rsplit(os.sep, 1)[0],
                    '%(base)s_%(w)dx%(h)d.jpg' % {
                        'base': str(imagePath.rsplit(os.sep, 1)[-1]).rsplit('.', 1)[0],
                        'w': thumbnailSize['width'],
                        'h': thumbnailSize['height']
                    }
                ),
                'size': [
                    thumbnailSize['width'],
                    thumbnailSize['height']
                ]
            }
            for thumbnailSize in self.ioSettings['display']['thumbnails']
        ]

        for thumbnailPathAndSize in thumbnailPathsAndSizes:

            self._generateThumbnail(
                imagePath,
                thumbnailPathAndSize['path'],
                thumbnailPathAndSize['size']
            )


        return thumbnailPathsAndSizes
    def setDisplayOrientation(self, orientation):
        """Set display orientation."""

        self.orientation = orientation


        return


    def _generateThumbnail(self, imagePath, thumbnailPath, size):
        """Format and save single thumbnail."""

        if not os.path.exists(thumbnailPath):

            thumbnailImage = self._profiledImageFromPath(imagePath, size)

            thumbnailImage.save(thumbnailPath)


        return
    def _profiledImageFromPath(self, imagePath, size):
        """Format image from path."""

        if size is None: size = self._displaySize()

        profiledImage = Image.open(imagePath).convert('RGB')
        profiledImage = ImageOps.exif_transpose(profiledImage)

        if self.ioSettings['display']['profile'] == 'fill':

            profiledImage = self._fillImage(
                profiledImage,
                size
            )

        elif self.ioSettings['display']['profile'] == 'fit|blur':

            bgImage = self._fillImage(
                profiledImage,
                size
            )
            bgImage = self._blurBrightenImage(bgImage)

            fgImage = self._fitImage(
                profiledImage,
                size
            )

            profiledImage = self._pasteImage(
                fgImage,
                bgImage
            )
            del bgImage
            del fgImage

        elif self.ioSettings['display']['profile'] == 'fit|color':

            bgImage = Image.new(
                mode='RGB',
                size=(
                    size[0],
                    size[1]
                ),
                color=(
                    self._fillColor()[0],
                    self._fillColor()[1],
                    self._fillColor()[2]
                )
            )

            fgImage = self._fitImage(
                profiledImage,
                size
            )

            profiledImage = self._pasteImage(
                fgImage,
                bgImage
            )
            del bgImage
            del fgImage


        return profiledImage

    def _quantizeImage(self, pilImage):
        """Quantize image from palette."""

        ditherImage = pilImage.copy()

        quantizedImage = ditherImage.quantize(
            palette=self.palette
        )


        return quantizedImage
    def _bufferImage(self, pilImage):
        """Buffer image for display."""

        displaySize = self._displaySize()

        imageRaw = bytearray(
            pilImage.tobytes('raw')
        )

        imageBuffered = [
            (imageRaw[int(r * 2)] << 4) + imageRaw[int((r * 2) + 1)]
            for r in range(int((displaySize[0] * displaySize[1]) / 2))
        ]


        return imageBuffered
    def _blurBrightenImage(self, pilImage):
        """Brighten and blur image."""

        bbImage = pilImage.copy()

        bbImage = bbImage.filter(
            ImageFilter.GaussianBlur(
                self._blurRadius()
            )
        )
        brightnessFilter = ImageEnhance.Brightness(bbImage)
        bbImage = brightnessFilter.enhance(
            self.ioSettings['display']['blur_brightness']
        )


        return bbImage
    def _fitImage(self, pilImage, size):
        """Fit image into available size."""

        fitImage = pilImage.copy()

        if fitImage.size[0] == size[0] and fitImage.size[1] == size[1]:

            return fitImage

        fitImage = fitImage.resize(
            (
                size[0] if (fitImage.size[0] / fitImage.size[1]) > (size[0] / size[1]) else int(fitImage.size[0] / fitImage.size[1] / size[1]),
                size[1] if (fitImage.size[0] / fitImage.size[1]) < (size[0] / size[1]) else int(fitImage.size[1] / fitImage.size[0] / size[0])
            ),
            Image.Resampling.LANCZOS
        )


        return fitImage
    def _fillImage(self, pilImage, size):
        """Fill image into available size."""

        fillImage = pilImage.copy()

        if fillImage.size[0] == size[0] and fillImage.size[1] == size[1]:

            return fillImage
        
        fillImage = fillImage.resize(
            (
                size[0] if (fillImage.size[0] / fillImage.size[1]) < (size[0] / size[1]) else int(fillImage.size[0] / fillImage.size[1] / size[1]),
                size[1] if (fillImage.size[0] / fillImage.size[1]) > (size[0] / size[1]) else int(fillImage.size[1] / fillImage.size[0] / size[0])
            ),
            Image.Resampling.LANCZOS
        )

        fillImage = self._cropImage(
            fillImage,
            x0=0 if (pilImage.size[0] / pilImage.size[1]) < (size[0] / size[1]) else int(
                (size[0] - fillImage.size[0]) / 2.0
            ),
            y0=0 if (pilImage.size[0] / pilImage.size[1]) > (size[0] / size[1]) else int(
                (size[1] - fillImage.size[1]) / 2.0
            ),
            x1=size[0] if (pilImage.size[0] / pilImage.size[1]) < (size[0] / size[1]) else int(
                ((size[1] - fillImage.size[1]) / 2.0) + size[0]
            ),
            y1=size[1] if (pilImage.size[0] / pilImage.size[1]) > (size[0] / size[1]) else int(
                ((size[1] - fillImage.size[1]) / 2.0) + size[1]
            )
        )


        return fillImage
    def _cropImage(self, pilImage, x0, y0, x1, y1):
        """Crop image."""

        croppedImage = pilImage.copy()

        croppedImage = croppedImage.crop(
            (
                x0,
                y0,
                x1,
                y1
            )
        )


        return croppedImage
    def _pasteImage(self, fgImage, bgImage, x=None, y=None):
        """Paste fgImage onto bgImage."""

        if x is None: x = int((bgImage.size[0] - fgImage.size[0]) / 2.0)
        if y is None: y = int((bgImage.size[1] - fgImage.size[1]) / 2.0)

        pastedImage = bgImage.copy()

        pastedImage.paste(
            fgImage,
            (
                x,
                y,
                x + fgImage.size[0],
                y + fgImage.size[1]
            )
        )


        return pastedImage
   

    def _generatePalette(self):
        """Generate quantization palette."""

        self.palette = Image.new(
            'P',
            (1, 1)
        )
        self.palette.putpalette(
            tuple(
                [
                    [
                        paletteColor['r'],
                        paletteColor['g'],
                        paletteColor['b']
                    ]
                    for paletteColor in sorted(self.ioSettings['display']['palette'], key=lambda c: c['id'])
                ] + [0, 0, 0] * (
                    256 - len(self.ioSettings['display']['palette'])
                )
            )
        )


        return
    def _fillColor(self):
        """Get fill color."""

        for paletteColor in self.ioSettings['display']['palette']:

            if paletteColor['fill'] == True:

                return [
                    paletteColor['r'],
                    paletteColor['g'],
                    paletteColor['b']
                ]


        return [255, 255, 255]
    def _displaySize(self):
        """Get display size."""

        displaySize = self.ioSettings['display']['size'][self._displayOrientation()]


        return [displaySize['width'], displaySize['height']]
    def _displayOrientation(self):
        """Get display orientation."""


        return self.orientation
    def _blurRadius(self):
        """Get image blur radius."""

        blurRadius = min(
            [
                2,
                int(
                    max(
                        self._displaySize()
                    ) / 32
                )
            ]
        )


        return blurRadius

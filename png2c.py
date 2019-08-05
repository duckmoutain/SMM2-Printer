#!/bin/python

import sys, os, getopt
from PIL import Image
def quantizetopalette(silf, palette, dither=False):
    """Convert an RGB or L mode image to use a given P image's palette."""

    silf.load()

    # use palette from reference image
    palette.load()
    if palette.mode != "P":
        raise ValueError("bad mode for palette image")
    if silf.mode != "RGB" and silf.mode != "L":
        raise ValueError(
            "only RGB or L mode images can be quantized to a palette"
            )
    im = silf.im.convert("P", 1 if dither else 0, palette.im)
    # the 0 above means turn OFF dithering

    # Later versions of Pillow (4.x) rename _makeself to _new
    try:
        return silf._new(im)
    except AttributeError:
        return silf._makeself(im)
def main(argv):
    opts, args = getopt.getopt(argv, "pshdm")
    previewBilevel = False
    saveBilevel = False
    ditherMode = False
    monochromeMode = False

    for opt, arg in opts:
        if opt == '-h':
          usage()
          sys.exit()
        elif opt == '-p':
            previewBilevel = True
        elif opt == '-s':
            saveBilevel = True
        elif opt == '-d':
            ditherMode = True
        
  
    paletteMap = {
        (0, 0, 0):1,
        (255, 255, 255):0,
        (188, 188,188):2,
        (188, 0, 138):3,
        (255, 194, 254):4,
        (136, 0, 188):5,
        (188, 98, 255):6,
        (0, 0, 254):7,
        (0, 255, 255):8,
        (0, 188, 0):9,
        (0, 255, 1):10,
        (254, 194, 0):11,
        (255, 255, 0):12,
        (173, 128, 71):13,
        (255, 245, 209):14,
        (188, 0, 0):15,
        (254, 0, 0):16,
    }

    palettedata = []

    for (k,v) in paletteMap.items():
        for i in range(3):
            palettedata += [k[i]]
    palettedata += [0]*3*(256-18)

    im = Image.open(args[0])                # import 320x180 png
    im = im.convert("RGB")
    if not (im.size[0] == 320 and im.size[1] == 180):
        print("ERROR: Image must be 320px by 180px!")
        sys.exit()

    palimage = Image.new('P', (16, 16))
    palimage.putpalette(palettedata)
    newimage = quantizetopalette(im, palimage, dither=ditherMode)
    if previewBilevel:
        newimage.show()
        #im.show()
    if saveBilevel:
        im.save("bilevel_" + args[0])
        print("Bilevel version of " + args[0] + " saved as bilevel_" + args[0])
    if not (previewBilevel or saveBilevel):
        im_px = newimage.convert('RGB').load()
        data = [0]
        # for i in range(0,120):                # iterate over the columns
        #     for j in range(0,320):              # and convert 255 vals to 0 to match logic in Joystick.c and invertColormap option
        #         print(paletteMap[im_px[j,i]])

        str_out = "#include <stdint.h>\n#include <avr/pgmspace.h>\n\nconst uint8_t image_data[] PROGMEM = {"
        # for i in range(0, (320*120) / 8):
        #    val = 0;

        #    for j in range(0, 8):
        #       val |= data[(i * 8) + j] << j

        #    if (invertColormap):
        #       val = ~val & 0xFF;
        #    else:
        #       val = val & 0xFF;

        #    str_out += hex(val) + ", "         # append hexidecimal bytes
        #                                       # to the output .c array
        # str_out += "0x0};\n"                  # of bytes

        byteIndex = 0
        offset = 0

        for i in range(0,160):
            for j in range(0,320):
                if offset <= 3:
                    c = paletteMap[im_px[j,i]]
                    data[byteIndex] |= (paletteMap[im_px[j,i]] << (3-offset))
                    if offset == 3:
                        byteIndex +=1
                        data.append(0)
                else:
                    data[byteIndex] |= (paletteMap[im_px[j,i]] >> (offset - 3))
                    byteIndex += 1
                    data.append(0)
                    data[byteIndex] |= ((paletteMap[im_px[j,i]] << (11 - offset)) & 0xFF)
                offset = (offset + 5) % 8
        print(data)

        for b in data:
            str_out += hex(b) + ", "
        str_out += "0x0};\n"
        with open('image.c', 'w') as f:       # save output into image.c
            f.write(str_out)
        if (ditherMode):
            print("{} converted with dithering mode and saved to image.c".format(args[0]))
        else:
            print("{} converted with average mode and saved to image.c".format(args[0]))

def usage():
    print("To convert to image.c: png2c.py <yourImage.png>")
    print("To convert to a image.c in dithering mode: png2c.py -d <yourImage.png>")
    print("To preview image: png2c.py -p <yourImage.png>")
    print("To save image: png2c.py -s <yourImage.png>")

if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        usage()
        sys.exit
    else:
        main(sys.argv[1:])

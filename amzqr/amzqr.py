#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from amzqr.mylibs import theqrmodule
from PIL import Image
   
# Positional parameters
#   words: str
#
# Optional parameters
#   version: int, from 1 to 40
#   level: str, just one of ('L','M','Q','H')
#   picutre: str, a filename of a image
#   colorized: bool
#   constrast: float
#   brightness: float
#   save_name: str, the output filename like 'example.png'
#   save_dir: str, the output directory
#   center_image: bool, if True, place the image in the center of QR code
#
# See [https://github.com/hwxhw/amazing-qr] for more details!
def run(words, version=1, level='H', picture=None, colorized=False, contrast=1.0, brightness=1.0, save_name=None, save_dir=os.getcwd(), center_image=False):

    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[]()?_{}|"


    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        raise ValueError('Wrong words! Make sure the characters are supported!')
    if not isinstance(version, int) or version not in range(1, 41):
        raise ValueError('Wrong version! Please choose a int-type value from 1 to 40!')
    if not isinstance(level, str) or len(level)>1 or level not in 'LMQH':
        raise ValueError("Wrong level! Please choose a str-type level from {'L','M','Q','H'}!")
    if picture:
        if not isinstance(picture, str) or not os.path.isfile(picture) or picture[-4:] not in ('.jpg','.png','.bmp','.gif'):
            raise ValueError("Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
        if picture[-4:] == '.gif' and save_name and save_name[-4:] != '.gif':
            raise ValueError('Wrong save_name! If the picuter is .gif format, the output filename should be .gif format, too!')
        if not isinstance(colorized, bool):
            raise ValueError('Wrong colorized! Input a bool-type value!')
        if not isinstance(contrast, float):
            raise ValueError('Wrong contrast! Input a float-type value!')
        if not isinstance(brightness, float):
            raise ValueError('Wrong brightness! Input a float-type value!')
    if save_name and (not isinstance(save_name, str) or save_name[-4:] not in ('.jpg','.png','.bmp','.gif')):
        raise ValueError("Wrong save_name! Input a filename tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
    if not os.path.isdir(save_dir):
        raise ValueError('Wrong save_dir! Input a existing-directory!')
    
        
    def combine(ver, qr_name, bg_name, colorized, contrast, brightness, save_dir, save_name=None, center_image=False):
        from amzqr.mylibs.constant import alig_location
        from PIL import ImageEnhance, ImageFilter
        
        qr = Image.open(qr_name)
        qr = qr.convert('RGBA') if colorized else qr
        
        bg0 = Image.open(bg_name).convert('RGBA')
        bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
        bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)

        if center_image:
            # 将图片放在二维码中央
            # 调整图片大小，使其适合放在二维码中央
            center_size = min(qr.size[0], qr.size[1]) // 3  # 中央图片大小为二维码的1/3
            
            if bg0.size[0] < bg0.size[1]:
                bg0 = bg0.resize((center_size, center_size * int(bg0.size[1]/bg0.size[0])))
            else:
                bg0 = bg0.resize((center_size * int(bg0.size[0]/bg0.size[1]), center_size))
            
            # 计算中央位置
            position = ((qr.size[0] - bg0.size[0]) // 2, (qr.size[1] - bg0.size[1]) // 2)
            
            # 创建一个新的透明图层
            qr_with_center = Image.new('RGBA', qr.size, (0, 0, 0, 0))
            qr_with_center.paste(qr, (0, 0))
            
            # 保护二维码的定位图案和关键信息区域
            from amzqr.mylibs.constant import alig_location
            
            # 获取定位图案的位置
            ver_act = (ver - 1) * 4 + 21
            box_size = ver_act // 21
            
            # 三个角落的定位图案
            patterns = [
                (0, 0, 7 * box_size, 7 * box_size),  # 左上
                (0, ver_act - 7 * box_size, 7 * box_size, ver_act),  # 左下
                (ver_act - 7 * box_size, 0, ver_act, 7 * box_size)   # 右上
            ]
            
            # 检查中央图片是否与定位图案重叠
            overlap = False
            for pattern in patterns:
                if (position[0] < pattern[2] and position[0] + bg0.size[0] > pattern[0] and
                    position[1] < pattern[3] and position[1] + bg0.size[1] > pattern[1]):
                    overlap = True
                    break
            
            # 如果不重叠，则粘贴中央图片
            if not overlap:
                qr_with_center.paste(bg0, position, bg0)
            
            qr = qr_with_center
        else:
            # 原来的融合逻辑
            if bg0.size[0] < bg0.size[1]:
                bg0 = bg0.resize((qr.size[0]-24, (qr.size[0]-24)*int(bg0.size[1]/bg0.size[0])))
            else:
                bg0 = bg0.resize(((qr.size[1]-24)*int(bg0.size[0]/bg0.size[1]), qr.size[1]-24))    
                
            bg = bg0 if colorized else bg0.convert('1')
            
            aligs = []
            if ver > 1:
                aloc = alig_location[ver-2]
                for a in range(len(aloc)):
                    for b in range(len(aloc)):
                        if not ((a==b==0) or (a==len(aloc)-1 and b==0) or (a==0 and b==len(aloc)-1)):
                            for i in range(3*(aloc[a]-2), 3*(aloc[a]+3)):
                                for j in range(3*(aloc[b]-2), 3*(aloc[b]+3)):
                                    aligs.append((i,j))

            for i in range(qr.size[0]-24):
                for j in range(qr.size[1]-24):
                    if not ((i in (18,19,20)) or (j in (18,19,20)) or (i<24 and j<24) or (i<24 and j>qr.size[1]-49) or (i>qr.size[0]-49 and j<24) or ((i,j) in aligs) or (i%3==1 and j%3==1) or (bg0.getpixel((i,j))[3]==0)):
                        qr.putpixel((i+12,j+12), bg.getpixel((i,j)))
        
        qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(bg_name))[0] + '_qrcode.png') if not save_name else os.path.join(save_dir, save_name)
        qr.resize((qr.size[0]*3, qr.size[1]*3)).save(qr_name)
        return qr_name

    tempdir = os.path.join(os.path.expanduser('~'), '.myqr')
    
    try:
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        ver, qr_name = theqrmodule.get_qrcode(version, level, words, tempdir)

        if picture and picture[-4:]=='.gif':
            import imageio
             
            im = Image.open(picture)
            duration = im.info.get('duration', 0)
            im.save(os.path.join(tempdir, '0.png'))
            while True:
                try:
                    seq = im.tell()
                    im.seek(seq + 1)
                    im.save(os.path.join(tempdir, '%s.png' %(seq+1)))
                except EOFError:
                    break
            
            imsname = []
            for s in range(seq+1):
                bg_name = os.path.join(tempdir, '%s.png' % s)
                imsname.append(combine(ver, qr_name, bg_name, colorized, contrast, brightness, tempdir, center_image=center_image))
            
            ims = [imageio.imread(pic) for pic in imsname]
            qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(picture))[0] + '_qrcode.gif') if not save_name else os.path.join(save_dir, save_name)
            imageio.mimwrite(qr_name, ims, '.gif', **{ 'duration': duration/1000 })
        elif picture:
            qr_name = combine(ver, qr_name, picture, colorized, contrast, brightness, save_dir, save_name, center_image=center_image)
        elif qr_name:
            qr = Image.open(qr_name)
            qr_name = os.path.join(save_dir, os.path.basename(qr_name)) if not save_name else os.path.join(save_dir, save_name)
            qr.resize((qr.size[0]*3, qr.size[1]*3)).save(qr_name)
          
        return ver, level, qr_name
        
    except:
        raise
    finally:
        import shutil
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
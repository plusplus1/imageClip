#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PIL import Image

_logger = logging.getLogger(__name__)


class ImageUtility(object):
    """
        image utility
    """

    _direction_horizontal = 'horizontal'
    _direction_vertical = 'vertical'

    _configs = {'pos': {
        _direction_vertical  : "竖着摆放",
        _direction_horizontal: "横着摆放", },

        'size'       : {'8寸' : (150, 200),
                        '10寸': (200, 250), }
    }

    _save_dpi = (300, 300)

    _save_kwargs = dict(quality=100, dpi=_save_dpi)

    @classmethod
    def show_info(cls, image_file):
        im_obj = Image.open(image_file)
        orig_size = im_obj.size
        info = im_obj.info
        width, height = orig_size[0], orig_size[1]
        # print(dir(im_obj))
        im_obj.close()
        _logger.info("file=%s\tsize=%s\tdpi=%s", image_file, (width, height),
                     info.get('dpi', None))

    @classmethod
    def try_clip(cls, image_file, output_dir, rotate_vertical=None, ref=None):
        """
        裁剪图片
        :param str image_file: 输入图片文件
        :param str output_dir: 输出目录
        :param bool rotate_vertical: 是否强制旋转成竖版
        :param tuple ref: 竖版目标尺寸，(宽度、高度）
        :return: 
        """
        ref_name = '8寸' if '8寸' in image_file else '10寸'
        if not ref:
            ref = cls._configs['size'][ref_name]

        assert ref and len(ref) == 2
        im_obj = Image.open(image_file)

        orig_size = im_obj.size
        width, height = orig_size[0], orig_size[1]

        if '竖版' in image_file:
            direction = cls._direction_vertical
        elif '横版' in image_file:
            direction = cls._direction_horizontal
        elif width > height:
            direction = cls._direction_horizontal
        else:
            direction = cls._direction_vertical

        if (direction == cls._direction_horizontal and width < height) or (
                        direction == cls._direction_vertical and width > height):
            ref_size = ref
        else:
            if width > height:
                ref_size = (ref[1], ref[0])
            else:
                ref_size = ref

        clip_height = int(width * (ref_size[1] / ref_size[0]))
        clip_width = int(height * (ref_size[0] / ref_size[1]))

        if clip_height > height:
            clip_size = (clip_width, height)
        else:
            clip_size = (width, clip_height)
        if clip_size[0] == width:
            delta = int((height - clip_size[1]) / 2)
            board = (0, delta, width, delta + clip_size[1])
        else:
            delta = int((width - clip_size[0]) / 2)
            board = (delta, 0, delta + clip_size[0], height)
            pass

        copped = im_obj.crop(board)
        if rotate_vertical and clip_size[0] > clip_size[1]:
            copped = copped.transpose(Image.ROTATE_90)

        output_file = "%s/%s-%s-%s" % (output_dir, ref_name, cls._configs['pos'][direction],
                                       str.rsplit(image_file, '/', 1)[1])
        copped.save(output_file, **cls._save_kwargs)
        logging.info("src=%s, \torig_size=%s\tclip_size=%s\tref=%s",
                     image_file, orig_size, clip_size, ref_size)

        im_obj.close()
        copped.close()
        pass

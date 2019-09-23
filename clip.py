#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import click
from PIL import Image

logging.basicConfig(level=logging.INFO)

_direction_horizontal = 'horizontal'
_direction_vertical = 'vertical'

_configs = {
    'pos' : {
        _direction_vertical  : "竖着摆放",
        _direction_horizontal: "横着摆放",
    },
    'size': {
        '8寸' : (122, 172),
        '10寸': (175, 225),
    }
}


def _try_clip_image(image_file, output_dir):
    ref_name = '8寸' if '8寸' in image_file else '10寸'
    ref = _configs['size'][ref_name]
    assert ref and len(ref) == 2

    im_obj = Image.open(image_file)
    orig_size = im_obj.size
    width, height = orig_size[0], orig_size[1]

    if '竖版' in image_file :
        direction = _direction_vertical 
    elif '横版' in image_file :
        direction = _direction_horizontal
    elif width > height :
        direction = _direction_horizontal 
    else:
        direction = _direction_vertical

    if (direction == _direction_horizontal and width < height) or (direction == _direction_vertical and width > height):
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
    if clip_size[0] > clip_size[1]:
        copped = copped.transpose(Image.ROTATE_90)

    copped.save("%s/%s-%s-%s" % (output_dir, ref_name, _configs['pos'][direction], str.rsplit(image_file, '/', 1)[1]),
                quality=100)
    logging.info("src=%s, \torig_size=%s\tclip_size=%s", image_file, orig_size, clip_size)
    pass


@click.command()
@click.option("--input", '-i', type=click.STRING, required=True, help='原始图片目录')
@click.option('--extension', '-e', default='jpg', required=True, help='图片格式')
@click.option("--output", '-o', type=click.STRING, required=True, help='输出图片目录')
def cli(**kwargs):
    """
    照片冲洗，按照要求尺寸进行图片裁剪
    """
    input_dir, ext = kwargs['input'], str.lower(kwargs['extension'])
    output_dir = kwargs['output']
    file_list = []
    for root_dir, _, fs in os.walk(input_dir):
        file_list += [os.path.join(root_dir, a_file) for a_file in fs
                      if str.endswith(a_file.lower(), ext)]
    for file in file_list:
        _try_clip_image(file, output_dir)

    return


if __name__ == '__main__':
    cli()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import click

logging.basicConfig(level=logging.INFO)

_context_settings = dict(help_option_names=['-h', '--help'])
_cmd_kwargs = dict(context_settings=_context_settings)
_default_options = dict(show_default=True, required=True)


@click.group(invoke_without_command=True, **_cmd_kwargs)
@click.option("--input", '-i', default='src', help='原始图片目录', **_default_options)
@click.option('--extension', '-e', default='jpg', help='图片格式', **_default_options)
@click.pass_context
def cli(ctx, **kwargs):
    """
    照片冲洗，按照要求尺寸进行图片裁剪
    """
    assert isinstance(ctx, click.Context)
    params = dict()
    params.update(**kwargs)
    ext = str.lower(kwargs['extension'])
    if not ext.startswith('.'):
        ext = '.' + ext
    input_dir = kwargs['input']
    file_list = []
    for root_dir, _, fs in os.walk(input_dir):
        file_list += [os.path.join(root_dir, name) for name in fs
                      if str.endswith(name.lower(), ext)]
        pass

    params['file_list'] = file_list

    ctx.obj = params
    if ctx.invoked_subcommand is None:
        ctx.invoke(info)
    return ctx


@cli.command()
@click.option("--output", '-o', default='out', help='输出图片目录', **_default_options)
@click.option('--rotate_vertical', '-r', is_flag=True, help='强制旋转竖版')
@click.option('--ref', type=click.STRING, help="输出宽高比，E.g: 150,200")
@click.pass_context
def clip(ctx, **kwargs):
    """批量裁剪"""
    from common.clip import ImageUtility
    output_dir = kwargs['output']
    rotate_vertical = kwargs['rotate_vertical']
    try:
        ref = tuple(map(int, str.split(kwargs['ref'], ',')))
        assert len(ref) == 2 and ref[0] > 0 and ref[1] > 0
    except (Exception,):
        ref = None

    logging.info('input_files: %d \t\toutput_dir=%s\trotate_vertical=%s\tref=%s',
                 len(ctx.obj['file_list']), output_dir, rotate_vertical, ref)

    util = ImageUtility()
    for filename in ctx.obj['file_list']:
        util.try_clip(filename, output_dir, rotate_vertical=rotate_vertical, ref=ref)
    return


@cli.command()
@click.pass_context
def info(ctx):
    """获取图像信息，尺寸（宽、高），分辨率"""
    from common.clip import ImageUtility
    logging.info('input_files: %d ', len(ctx.obj['file_list']))

    util = ImageUtility()
    for filename in ctx.obj['file_list']:
        util.show_info(filename)
    return


if __name__ == '__main__':
    cli()

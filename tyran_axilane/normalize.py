# coding: utf-8
from __future__ import print_function

import io
import logging
import os.path

from tyran_axilane.converters import CONVERTERS

LOG = logging.getLogger(__name__)


def normalize(src_path, dst_path):
    dst_dir, dst_name = os.path.split(dst_path)
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)

    basename = os.path.basename(dst_name)
    log_name = f"{basename}.log"
    log_path = os.path.join(dst_dir, log_name)
    logging.basicConfig(level=logging.INFO,
                        format="{levelname:<7} {name}: {message}",
                        filename=log_path,
                        style='{')

    LOG.info("Reading file '{0}'...".format(src_path))
    with io.open(src_path, mode="r", encoding='utf-8') as f:
        content = f.read()

    for counter, (converter_name, converter) in enumerate(CONVERTERS, 1):
        name = f"{counter:02d}_{converter_name}.html"
        path = os.path.join(dst_dir, name)
        LOG.info(f"Running {converter_name}...")
        content = converter(content)
        with io.open(path, mode="w", encoding="utf-8") as f:
            f.write(content)

    with io.open(dst_path, mode="w", encoding="utf-8") as f:
        f.write(content)


if __name__ == '__main__':
    normalize("tyran_axilane.txt", "../target/tyran_axilane.html")

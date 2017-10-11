import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    # Use distutils.core as a fallback.
    # We won't be able to build the Wheel file on Windows.
    from distutils.core import setup

if sys.version_info < (3, 5, 0):
    raise RuntimeError("achihuo-mini requires Python 3.5.0+")

version = "0.2.0"

requires = [
    "redis",
    "pymysql",
    "pika",
    "mugen",
]

setup(
    name="achihuo-mini",
    version=version,
    author="dingfanghong",
    author_email="fanghong.ding@lejent.com",
    license="Apache 2.0",

    description="Achihuo - Mini Version, For Asynchronous Spider",
    url="http://git.lejent.cn/Spider/achihuo_mini",

    install_requires=requires,

    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],

    packages=find_packages(),
)

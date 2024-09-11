import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    "pyserial",
    "pyvisa",
    "numpy",
    "PyVISA-py",
    "psutil",
    "zeroconf",
]


# Get the absolute path to the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "src/pytools_hardware_control/__about__.py"), "r") as f:
    about = {}
    exec(f.read(), about)


setuptools.setup(
    include_package_data=True,
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=[about["__title__"]],
    package_dir={"": "src"},
    install_requires=install_requires,
)

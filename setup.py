import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytools_hardware_control",
    version="0.0.3",
    author="Nynra & D.D. Land",
    author_email="nynradev@pm.me",
    description="Library of classes usefull working in the lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["pytools_hardware_control"],
    package_dir={"": "src"},
    install_requires=[
        "pyserial",
        "pyvisa",
        "numpy",
        "PyVISA-py",
        "psutil",
        "zeroconf",
    ],
)
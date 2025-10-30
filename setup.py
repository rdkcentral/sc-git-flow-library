import setuptools

def read_version():
    with open("VERSION", "r") as f:
        return f.read().strip()

setuptools.setup(
    name="git_flow_library",
    version=read_version(),
    author="RDK Management",
    description="A collection of utility for standardising gitflow commands in python.",
    packages=setuptools.find_packages(),
)
from setuptools import setup, find_packages

setup(
    name='kissBT',
    version="1.0.0",
    # packages=["kissBT"],
    packages=find_packages(),
    url='https://github.com/UniBwTAS/kissBT',
    author='Thomas Steinecker',
    author_email='thomas.steinecker@unibw.de',
    include_package_data=True,
    description="A very basic behavior tree implementation for Python",
)
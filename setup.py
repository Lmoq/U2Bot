from setuptools import setup, find_packages

setup(
    name = "U2",
    version = "0.1",
    # Finds 'mymodule' and subpackages
    packages = find_packages(),
    # Include non-code files like .sh
    # listed in MANIFEST.in
    include_package_data=True,  
)

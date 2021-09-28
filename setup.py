from setuptools import setup, find_packages


with open("README.md", "r") as readme_file:
    readme_text = readme_file.read()


setup_args = dict(
    name='omoide-cache',
    version='0.1.2',
    description="Robust, highly tunable and easy-to-integrate in-memory cache solution written in pure Python, with no dependencies.",
    keywords=['cache', 'decorator', 'annotation', 'in-memory'],
    license='Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License',
    long_description=readme_text,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Leo Ertuna",
    author_email="leo.ertuna@gmail.com",
    url="https://github.com/jpleorx/omoide-cache",
    download_url='https://pypi.org/project/omoide-cache/'
)


install_requires = []


if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)

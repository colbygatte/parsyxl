from setuptools import setup

setup(name='parsyxl',
      version='0.0.1',
      description='Tools built around the parsy library.',
      url='http://github.com/colbygatte/parsyxl',
      author='Colby Gatte',
      author_email='colbygatte@gmail.com',
      license='MIT',
      packages=['parsyxl'],
      zip_safe=False,
      install_requires=[
            'parsy',
            'attr'
      ])

from setuptools import setup, find_packages

# https://www.digitalocean.com/community/tutorials/how-to-package-and-distribute-python-applications

setup(
    name="really-simple-bbs",
    version="0.1",

    description='''A really simple BBS developed particularly with ax.25 and amateur radio in mind.''',

    author='John Burwell',
    author_email='john@atatdotdot.com',

    url='https://git.b-wells.us/jmbwell/rsbbs',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],


    packages=find_packages(exclude=['test*', 'Test*']),

    package_data={
        '': ['README.md', 'LICENSE'],
        'really-simple-bbs': ['config.yaml.sample']
      },


    scripts=['main.py'],

    entry_points={
          'console_scripts': [
              'main.py = main:main',
          ],
      },

    install_requires=[
        'greenlet==2.0.2',
        'PyYAML==6.0',
        'SQLAlchemy==2.0.10',
        'typing_extensions==4.5.0',
      ],


)
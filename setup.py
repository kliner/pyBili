from distutils.core import setup

setup(
  name = 'pybili',
  packages = ['pybili'], # this must be the same as the name above
  version = '0.1',
  description = 'A helper library for bilibili.com',
  author = 'Kliner',
  author_email = 'kliner@live.cn',
  url = 'https://github.com/kliner/pyBili', # use the URL to the github repo
  download_url = 'https://github.com/kliner/pyBili/archive/0.1.1.tar.gz', # I'll explain this in a second
  keywords = ['bili', 'live', 'danmaku'], # arbitrary keywords
  classifiers = [],

  install_requires=['requests'],

  entry_points={
    'console_scripts':[
      'bili-danmuji = pybili.DanMuJi:main',
      'bili-music = pybili.AutoDianGeJi:main',
      'bili-sender = pybili.bili_sender:main',
    ]
  }
)

from distutils.core import setup
import pybili

setup(
  name = 'pybili',
  packages = ['pybili'], # this must be the same as the name above
  version = pybili.__version__,
  description = 'A helper library for bilibili.com',
  author = 'Kliner',
  author_email = 'kliner@live.cn',
  url = 'https://github.com/kliner/pyBili', # use the URL to the github repo
  download_url = 'https://github.com/kliner/pyBili/archive/%s.tar.gz' % pybili.__version__,
  keywords = ['bili', 'live', 'danmaku'], # arbitrary keywords
  classifiers = [],

  install_requires=['requests', 'pymongo', 'emoji_list'],

  entry_points={
    'console_scripts':[
      'bili-danmuji = pybili.GUI:main',
      'bili-dm = pybili.DanMuJi:main',
      'bili-music = pybili.AutoDianGeJi:main',
      'bili-sender = pybili.bili_sender:main',
      'bili-config = pybili.bili_config:main',
    ]
  }
)

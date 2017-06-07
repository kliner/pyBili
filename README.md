# pyBili

This is a python live.bilibili.com helper library.

# Function

* Danmaku receiver / sender with GUI support.
* Auto join SmallTV.
* Mac Notification / TTS.
* A basic music VOD.
* Gift auto response.
* Easy to add new functions.

# Install

`$ sudo pip install pybili`

# Usage

1. Please create a file '.pybili.conf' in your home directory(~).

    ```
    [cookies]
    cookies=your_cookie
    
    [90012]
    GiftResponse=false
    ShowTime=false
    SmallTVHint=false
    MacNotification=false
    MacTTS=false
    DanmakuColor=blue
    ```

    Also you can use 

    `$ bili-config`

    to setup this config file.

2. Run from your favorite shell.

    `$ bili-danmuji roomid`

# Note

1. How to get the cookies?

    ![get cookies](/images/get_cookies.png)
    
2. How to use the Mac notification? Get an error `/bin/sh: terminal-notifier: command not found`?

    Install the terminal-notifier through 
    
    `$ brew install terminal-notifier`

3. How to record the danmakus?

    Install the MongoDB through

    `$ brew install mongodb[1](https://docs.mongodb.com/master/tutorial/install-mongodb-on-os-x/)`

# License (MIT)

Copyright (c) 2017-2017 kliner

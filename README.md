# pyBili

This is a python live.bilibili.com helper library.

# Function

* Danmaku receiver / sender.
* Auto join SmallTV.
* Mac Notification / TTS.
* A basic music VOD.
* Gift auto response.
* Easy to add new functions.

# Install

`$sudo pip install pybili`

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

2. Run from your favorite shell.

    `$bili-danmuji roomid`

# Note

1. How to get the cookies?

    ![get cookies](/images/get_cookies.png)

# License (MIT)

Copyright (c) 2017-2017 kliner

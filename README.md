# pyBili

This is a python live.bilibili.com helper library.

# Function

* Danmaku helper with GUI.
* Mac Notification/TTS.
* A basic music VOD.
* Auto join/response SmallTV.

# Install

`$ pip install pybili`

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

    `$ brew install mongodb` [more](https://docs.mongodb.com/master/tutorial/install-mongodb-on-os-x/)

4. How to use the web-interface?

    1. Install RabbitMQ(connection between this project and the Live-Stream-Chat-Retriever project:

        `$ brew install rabbitmq` [more](https://www.rabbitmq.com/#getstarted/)

    2. Setup aonther project from [https://github.com/kliner/Live-Stream-Chat-Retriever](https://github.com/kliner/Live-Stream-Chat-Retriever), or using:

        `$ npm install https://github.com/kliner/Live-Stream-Chat-Retriever/archive/0.1.0.tar.gz`

    3. Using 2 shells to run 

        `$ bili-dm roomId`

        `$ npm start PATH_TO_{Live-Stream-Chat-Retriever}`

# License (MIT)

Copyright (c) 2017-2017 kliner

# Japanese_ChatBot_with_ParlAI
## 1. Description
This is a Japanese chat bot based on the ParlAI by Facebook. You can communicate to the chat bot by keyboard and/or voice.  If you want to enjoy conversation in English, please check the "[ChatBot_with_ParlAI](https://github.com/To-Fujita/ChatBot_with_ParlAI)".

## 2. Operational Environment
- Windows 10/11 64-bit
- Visual Studio Code (VS Code)
- Python 3.9.4 64-bit
- Browser: Microsoft Edge or Google Chrome

## 3. Demo

## 4. Details
I have confirmed this Python Script on the above conditions only. I will show you below how to execute the Python Script.

### 4-1. Preparation
(a) Download and unzip the file.  
Please download following files and put the unzipped folders under the system path passed.
- [ParlAI](https://github.com/facebookresearch/parlai): A framework for training and evaluating AI models on a variety of openly available
- Japanese_ChatBot_with_ParlAI: Please download from above "Code".
  
(b) Install some libraries to your Python  
- Pytorch: pip install torch
- ParlAI: pip install parlai
- Janome: pip install janome
- Flask: pip install Flask

### 4-2. Try to communicate with the chat bot
The Chat Bot program is as follows.
- main_JP_tiny.py
or
- main_JP_Voicevox_tiny.py (If you try to run this script, please run the VOICEVOX program first.)
Please open the above file on the VS Code, then click the "Run" and the "Start Debugging" or the "Run Without Debugging". Wait a few minutes, it will be displayed "*Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)" at the Terminal. Then, after open the Browser, please input "http://127.0.0.1:5000". You can talk with the Chat Bot by keybord and/or voice.
  
If this script is not working well, please check your setting for system path and/or check your Python environment. When you run the Rinna for the first time, it takes a few minutes to download various files.
  
This Chat Bot is created in following concepts.

- The human interface is given in HTML and JavaScript.
- The answer from the chat bot is created in Python.
In this time, I used the "Dialog Element" in HTML. The Safari and the FireFox are not supported for the Dialog Element, yet. Therefor, it is not working well by the Safari and the FireFox. Please enjoy the talk with the Chat Bot on the Microsoft Edge or the Google Chrome. 

## 5. Reference
- [ParlAI](https://www.parl.ai/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/)
- [VOICEVOX](https://voicevox.hiroshiba.jp/) : 無料で使える中品質なテキスト読み上げソフトウェア

## 6. License
- Programs: MIT
- All of the images and ParlAI: Please confirm to each author.

## 7. Author
[T. Fujita](https://github.com/To-Fujita/)

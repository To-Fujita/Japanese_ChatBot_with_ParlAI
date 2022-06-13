# ChatBot with ParlAI and VoiceVox, "main_JP_Voicevox_tiny.py" by F. Fujita on 2022/05/24

import sys
sys.path.append('./ParlAI-main/')

import random
import difflib
from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent, Agent
from parlai.core.worlds import create_task
from parlai.core.script import ParlaiScript, register_script
from parlai.core.opt import Opt
from parlai.core.message import Message
from parlai.utils.misc import load_cands
from typing import Optional
from chardet.universaldetector import UniversalDetector
from flask import Flask, render_template, request
from janome.tokenizer import Tokenizer
from modules import RSS_Recieve_01
import json
import requests
import wave


agent = ''
human_agent = ''
opt_org = ''
file_path = './Japanese_ChatBot_with_ParlAI-main/'            # 貴方の環境に合わせてパス設定を変更してください。
CSV_file = file_path + 'data/Talk_List.csv'
news_file = file_path + 'data/News.csv'
tenki_file = file_path + 'data/Tenki_jp.csv'
Model_file= file_path + 'model_tiny/model'
Dict_file= file_path + 'model_tiny/model.dict'
Unk_data= 'あのね、'
app = Flask(__name__, static_url_path='/static')
tokenizer = Tokenizer()
t_wakati = Tokenizer(wakati=True)
area_name = '日本'
answer_data = []
ai_ratio = 0.5
Speaker_No = 0
voice_count = 0
filepath = file_path + 'static/audio/audio'

@app.route("/")
# Display by the HTML
def home():
    return render_template("index_JP_Voicevox_tiny.html")

@app.route("/get_New")
def csv_New():
    global answer_data
    answer_data = list()
    answer_data = []
    temp_data = request.args.get('new_CSV')
    temp = temp_data.split('%0D%0A')
    for i in range(len(temp)):
        temp_01 = temp[i].split('\r\n')
        for j in range(len(temp_01)):
            temp_02 = temp_01[j].split(',')
            if (temp_02[0] != ""):
                temp_02.append('\r\n')
                answer_data.append(temp_02)
    return ('OFF')

@app.route("/get_Add")
def csv_Add():
    global answer_data
    temp_data = request.args.get('add_CSV')
    temp = temp_data.split('%0D%0A')
    for i in range(len(temp)):
        temp_01 = temp[i].split('\r\n')
        for j in range(len(temp_01)):
            temp_02 = temp_01[j].split(',')
            if (temp_02[0] != ""):
                temp_02.append('\r\n')
                answer_data.append(temp_02)
    return ('OFF')

@app.route("/get_Save")
def csv_Save():
    temp_CSV = ""
    for i in range(len(answer_data)):
        for j in range(len(answer_data[i])):
            if (j==0):
                temp_CSV = temp_CSV + answer_data[i][j]
            elif (answer_data[i][j] != ""):
                temp_CSV = temp_CSV + "," + answer_data[i][j]
    temp_data = request.args.get('save_CSV')
    if (temp_data == "CSV_Save"):
        return temp_CSV
    else:
        return ("OFF")

@app.route("/get_AI_Ratio")
# Get the AI Ratio from HTML
def get_AI_Ratio():
    global ai_ratio
    ai_ratio = float(request.args.get('AI_Ratio'))/100
    return (str('OK'))

@app.route("/get_Voice")
# Get the Voice No from HTML
def get_Voice_No():
    global Speaker_No
    Speaker_No = int(request.args.get('Voice_No'))
    return (str('OK'))

@app.route("/get")
# Communicate with HTML
def get_bot_response():
    userText = request.args.get('msg')
    answer = make_answer(userText)
    return answer

# Create the answer
def make_answer(tempText):
    global voice_count
    voice_count = voice_count + 1
    if (voice_count >= 30000):
        voice_count = 0
    voice_count_text = ('0000' + str(voice_count))[-4:]

    if (tempText == ""):
        tempText = "　"
    global area_name
    kensaku_Word = 'ウィキペディア'
    for token in tokenizer.tokenize(tempText):
        if token.part_of_speech.split(',')[2] == '地域':
            area_name = token.surface
        if token.part_of_speech.split(',')[0] == '名詞':
            if (kensaku_Word == 'ウィキペディア' or token.surface != '検索'):
                if (token.surface != '何'):
                    kensaku_Word = token.surface
    wakati = list(t_wakati.tokenize(tempText))
    if ('について検索' in tempText):
        kensaku_Word = tempText[0: tempText.find('について検索')]
    if ('の写真' in tempText):
        kensaku_Word = tempText[0: tempText.find('の写真')]
    if ('の画像' in tempText):
        kensaku_Word = tempText[0: tempText.find('の画像')]
    if ('の動画' in tempText):
        kensaku_Word = tempText[0: tempText.find('の動画')]
    if ('の映像' in tempText):
        kensaku_Word = tempText[0: tempText.find('の映像')]
    if ('のビデオ' in tempText):
        kensaku_Word = tempText[0: tempText.find('のビデオ')]
    if ('の鳴き声' in tempText):
        kensaku_Word = tempText[0: tempText.find('の鳴き声')]
    if ('の地図' in tempText):
        kensaku_Word = tempText[0: tempText.find('の地図')]
    if ('のマップ' in tempText):
        kensaku_Word = tempText[0: tempText.find('のマップ')]
    if ('のレシピ' in tempText):
        kensaku_Word = tempText[0: tempText.find('のレシピ')]
    if ('の調理法' in tempText):
        kensaku_Word = tempText[0: tempText.find('の調理法')]
    if ('の料理の仕方' in tempText):
        kensaku_Word = tempText[0: tempText.find('の料理の仕方')]
     
    if (('音声認識' in tempText or '音声入力' in tempText) and '終了' in tempText):
        return str('音声入力を終了しました。')
    else:
        temp_Answer = PatternResponder(tempText)
        if ('#NEWS#' in temp_Answer):
            temp = RSS_Recieve_01.news(news_file)
            temp_Answer = temp_Answer.replace('#NEWS#', temp)
        if ('#WEATHER#') in temp_Answer:
            temp_Answer = RSS_Recieve_01.tenki(area_name, tenki_file)
        if ('#WIKI#') in temp_Answer:
            if (kensaku_Word == 'ウィキペディア'):
                for i in range(1, len(wakati) - 1):
                    if (wakati[i] == 'を' or wakati[i] == 'とは' or wakati[i] == '永遠'):
                        kensaku_Word = wakati[i-1]
                    if (wakati[i] == 'について'):
                        kensaku_Word = tempText[0: tempText.find('について')]
            temp = RSS_Recieve_01.kensaku(kensaku_Word)
            temp_Answer = kensaku_Word + 'の検索結果は、' + temp_Answer.replace('#WIKI#', temp)
        if ('#FORTUNE#') in temp_Answer:
            temp_Answer = '占いを表示します。'
        if ('#PHOTO#') in temp_Answer:
            temp_Answer = kensaku_Word + 'の画像を表示します。'
        if ('#VIDEO#') in temp_Answer:
            temp_Answer = kensaku_Word + 'のビデオを表示します。'
        if ('#CALL#') in temp_Answer:
            temp_Answer = kensaku_Word + 'ですね、鳥以外には対応していません。動物の鳴き声は「東京ズーネット」で検索してください。'
        if ('#MAP#') in temp_Answer:
            temp_Answer = kensaku_Word + 'の地図を表示します。'
        if ('#RECIPE#') in temp_Answer:
            temp_Answer = kensaku_Word + 'のレシピを表示します。'
        
        generate_wav(temp_Answer, Speaker_No, filepath, voice_count_text)      
        return str(voice_count_text + ':' + temp_Answer)

# ChatBot
class LocalHumanAgent(Agent):
    @classmethod
    def add_cmdline_args(
        cls,
        parser: ParlaiParser,
        partial_opt: Optional[Opt] = None,
    ) -> ParlaiParser:

        agent = parser.add_argument_group('Local Human Arguments')
        agent.add_argument(
            '-fixedCands',
            '--local-human-candidates-file',
            default=None,
            type=str,
            help='File of label_candidates to send to other agent',
        )
        agent.add_argument(
            '--single_turn',
            type='bool',
            default=False,
            help='If on, assumes single turn episodes.',
        )
        return parser

    def __init__(self, opt, shared=None):
        super().__init__(opt)
        self.id = 'localHuman'
        self.episodeDone = False
        self.finished = False
        self.fixedCands_txt = load_cands(self.opt.get('local_human_candidates_file'))

    def observe(self, msg):
        global text_reply
        text_reply = msg["text"]
        return text_reply

    def act(self):
        global text_send
        reply = Message()
        reply['id'] = self.getID()
        reply_text = text_send
        reply_text = reply_text.replace('\\n', '\n')
        reply['episode_done'] = False
        reply['text'] = reply_text
        return reply

def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(
            True, True, 'Interactive chat with a model on the command line'
        )
    parser.add_argument('-d', '--display-examples', type='bool', default=False)
    parser.add_argument(
        '--display-prettify',
        type='bool',
        default=False,
        help='Set to use a prettytable when displaying '
        'examples with text candidates',
    )
    parser.add_argument(
        '--display-add-fields',
        type=str,
        default='',
        help='Display these fields when verbose is off (e.g., "--display-add-fields label_candidates,beam_texts")',
    )
    parser.add_argument(
        '-it',
        '--interactive-task',
        type='bool',
        default=True,
        help='Create interactive version of task',
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='',
        help='Saves a jsonl file containing all of the task examples and '
        'model replies. Set to the empty string to not save at all',
    )
    parser.add_argument(
        '--save-format',
        type=str,
        default='conversations',
        choices=['conversations', 'parlai'],
        help='Format to save logs in. conversations is a jsonl format, parlai is a text format.',
    )
    parser.set_defaults(interactive_mode=True, task='interactive')
    LocalHumanAgent.add_cmdline_args(parser, partial_opt=None)
    return parser

def interactive(opt):
    global agent
    global human_agent
    global opt_org

    if isinstance(opt, ParlaiParser):
        opt = opt.parse_args()

    agent = create_agent(opt, requireModelExists=True)
    human_agent = LocalHumanAgent(opt)
    world = create_task(opt, [human_agent, agent])
    opt_org = opt

@register_script('interactive', aliases=['i'])
class Interactive(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return interactive(self.opt)


text_send = ''
text_reply = ''
select_no = 0
id_no = ''

def in_out(temp_text):
    global text_send
    global text_reply
    text_send = temp_text
    world = create_task(opt_org, [human_agent, agent])
    world.parley()
    return text_reply

def init():
    global answer_data
    answer_data = []
    temp_data = csv_load(CSV_file)
    for i in range(len(temp_data)):
        temp = temp_data[i].split(',')
        if (temp[0] != ""):
            temp_temp = []
            for j in range(len(temp)):
                if (temp[j] != "" or temp[j] != "\r\n" or temp[j] != "\n"):
                   temp_temp.append(temp[j])
            answer_data.append(temp_temp)
    Interactive.main(
        task= 'blended_skill_talk',
        model_file= Model_file,
        dict_file= Dict_file,
        include_personas= False,
    )
    return

def csv_load(filename):
    lines = []
    file_code = detect_character_code(filename)
    with open (filename, encoding=file_code) as csvfile:
        for line in csvfile.readlines():
            lines.append(line)
    return lines

def detect_character_code(pathname):
    file_code_dic = ''
    detector = UniversalDetector()
    with open (pathname, 'rb') as f:
        detector.reset()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        file_code_dic = detector.result['encoding']
    return file_code_dic

def PatternResponder(tempText):
    temp_count = 0.0
    max_count = 0.0
    array_No = 0
    for i in range(len(answer_data)):
        temp_count = difflib.SequenceMatcher(None, tempText, answer_data[i][0]).ratio()
        if (max_count < temp_count):
            max_count = temp_count
            array_No = i
    #print('質問一致率＝ ', max_count)
    temp_Answer = random.choice(answer_data[array_No])
    if (temp_Answer == answer_data[array_No][0] or temp_Answer == "" or temp_Answer == " " or temp_Answer == "\n"):
        temp_Answer = answer_data[array_No][1]
    if ('#') in temp_Answer:
        return temp_Answer
    elif (array_No > len(answer_data)) or (max_count <= ai_ratio):
        temp_Answer = in_out(str(tempText))
        temp_Answer = temp_Answer.replace(' ', '')
        temp_Answer = temp_Answer.replace('__unk__', Unk_data)
    return temp_Answer

def generate_wav(text, speaker, filepath, voice_count_text):
    filepath = filepath + voice_count_text + '.wav'
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    headers = {'Content-Type': 'application/json',}
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json())
    )

    wf = wave.open(filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(response2.content)
    wf.close()

if __name__ == "__main__":
    random.seed(None)
    init()
    app.run(host='127.0.0.1', port=5000, debug=True)

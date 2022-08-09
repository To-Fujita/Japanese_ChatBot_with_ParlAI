# ChatBot with ParlAI, "main_JP_tiny.py" by F. Fujita on 2022/06/30

import sys
sys.path.append('./ParlAI-main/')                   # Please set the PATH name according to your environment.

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

agent = ''
human_agent = ''
opt_org = ''
file_path = './Japanese_ChatBot_with_ParlAI-main/'       # Please set the PATH name according to your environment.
CSV_file = file_path + 'data/Talk_List.csv'
news_file = file_path + 'data/News.csv'
tenki_file = file_path + 'data/Tenki_jp.csv'
link_file = file_path + 'data/Link_List.csv'
Model_file= file_path + 'model_tiny/model'
Dict_file= file_path + 'model_tiny/model.dict'
Unk_data= 'えぇーと、'
app = Flask(__name__, static_url_path='/static')
tokenizer = Tokenizer()
t_wakati = Tokenizer(wakati=True)
area_name = '日本'
answer_data = []
link_data = []
ai_ratio = 0.5

@app.route("/")
# Display by the HTML
def home():
    return render_template("index_JP.html")

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

@app.route("/get")
# Communicate with HTML
def get_bot_response():
    userText = request.args.get('msg')
    answer = make_answer(userText)
    return answer

# Create the answer
def make_answer(tempText):
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
    for i in range(0, len(link_data)):
        if (link_data[i][1] in tempText):
            kensaku_Word = tempText[0: tempText.find(link_data[i][1])]
    
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
        temp_Answer = kensaku_Word + 'の検索結果は、' + temp_Answer.replace('#WIKI#', temp) + "https://ja.wikipedia.org/wiki/" + kensaku_Word
    elif ('#') in temp_Answer:
        temp_data = temp_Answer
        for i in range(0, len(link_data)):
            if link_data[i][0] in temp_Answer:
                temp_data = link_data[i][2] + link_data[i][3] + link_data[i][4] + link_data[i][5]
            temp_data = temp_data.replace('$NON$', '')
            temp_data = temp_data.replace('$KEY$', kensaku_Word)
        temp_Answer = temp_data
    return str(temp_Answer)

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
    global link_data
    answer_data = []
    answer_data = csv_load(CSV_file)
    link_data = []
    link_data = csv_load(link_file)
    
    Interactive.main(
        task= 'blended_skill_talk',
        model_file= Model_file,
        dict_file= Dict_file,
        include_personas= False,
    )
    return

def csv_load(filename):
    lines = []
    return_data = []
    file_code = detect_character_code(filename)
    with open (filename, encoding=file_code) as csvfile:
        for line in csvfile.readlines():
            lines.append(line)
    for i in range(len(lines)):
        temp = lines[i].split(',')
        if (temp[0] != ""):
            temp_data = []
            for j in range(len(temp)):
                if (temp[j] != "" or temp[j] != "\r\n" or temp[j] != "\n"):
                    temp_data.append(temp[j])
            return_data.append(temp_data)
    return return_data

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

if __name__ == "__main__":
#    random.seed(None)
    init()
    app.run(host='127.0.0.1', port=5000, debug=True)

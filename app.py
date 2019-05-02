from flask import Flask, render_template, request
from flask_cors import CORS
from service.ApiService import top5questions, latest5questions, sentence_search, get_question_detail, \
    get_total_questions

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 用于处理跨域问题


def render_index():
    top = top5questions()
    latest = latest5questions()
    total = get_total_questions()
    return render_template('index.html', top=top, latest=latest, total=total)


# 首页
@app.route('/')
def index():
    return render_index()


# 首页
@app.route('/index')
def index2():
    return render_index()


@app.route('/detail/<qid>')
def detail(qid):
    qa = get_question_detail(qid)
    total = get_total_questions()
    return render_template('detail.html', qa=qa, total=total)


@app.route('/ask', methods=['POST'])
def list():
    question = request.form['question']
    questions = sentence_search(question)
    total = get_total_questions()
    result_size = len(questions)
    return render_template('list.html', questions=questions, total=total, result_size=result_size)


def start_flask():
    app.run(threaded=True)


if __name__ == '__main__':
    start_flask()

#encoding: utf-8

from flask import Flask,render_template,request,redirect,url_for,session,g
from models import User, Questions, Answer
from exts import db
import config
import sys
from sqlalchemy import or_

# reload(sys)
# sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


# @app.route('/')
# def hello():
#     return redirect(url_for('index'))


@app.route('/')
def index():
    context = {
        'questions': Questions.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号码或密码错误，请确认后再登陆'


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        print(telephone,username,password1,password2)
        # 手机号码验证，如果注册了，就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号已注册，请更换手机号码！'
        else:
            if password1 != password2:
                return u'2次密码不相同，请核对后再填写！'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登录页面
                return redirect(url_for('login'))

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    # session.pop('user_id')
    # del session['user_id']
    session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
# @login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        # user_id = session.get('user_id')
        # user = User.query.filter(User.id == user_id).first()
        user = g.user
        questions = Questions(title=title, content=content)
        questions.author = user
        db.session.add(questions)
        db.session.commit()
        # print("---------------------------------------------")
        # return render_template('index.html')
        return redirect(url_for('index'))


@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Questions.query.filter(Questions.id == question_id).first()
    return render_template('detail.html', question=question_model)


@app.route('/add_answer/', methods=['POST'])
# @login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content)
    # user_id = session.get('user_id')
    # user = User.query.filter(User.id == user_id).first()
    # answer.author = user
    answer.author = g.user
    question = Questions.query.filter(Questions.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


@app.route('/search/')
def search():
    q = request.args.get('q')
    # title content
    # 或
    condition = or_(Questions.title.contains(q), Questions.content.contains(q))
    questions = (Questions.query.filter(condition).order_by('-create_time'))
    #与
    # questions = Questions.query.filter(Questions.title.contains(q), Questions.content.contains(q))
    return render_template('index.html', questions=questions)

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user



@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    return {}

if __name__ == '__main__':
    app.run()

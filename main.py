import flask
import json
import  os
from flask import Flask,render_template,session,redirect
from flask_sqlalchemy import SQLAlchemy,request
from flask_mail import  Mail
from werkzeug import secure_filename


with open('config.json' , 'r') as c:
    params=json.load(c)["params"]

local_server=True

app = Flask(__name__)
app.secret_key='super_secret_key'
app.config['UPLOAD_FOLDER']=params['upload_location']


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']



# creete databse connection

db = SQLAlchemy(app)


# subbmmit value from db

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), nullable=False)
    passw = db.Column(db.String(120), nullable=False)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(120), nullable=False)
    tag= db.Column(db.String(120), nullable=False)
    slug= db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date= db.Column(db.String(12), nullable=False)
    img= db.Column(db.String(12), nullable=False)






@app.route("/")
def home():
    post=Post.query.filter_by().all()
    return render_template("index.html",post=post)















@app.route("/contact", methods=['GET','POST'])
def contact():
    if (request.method == "POST"):
        name = request.form.get('name')
        pas = request.form.get('password')
        entry =Contacts(name=name , passw=pas)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=name,
                          recipients=[params['gmail-user']],
                          body=pas
                          )

    return render_template("contact.html")





@app.route("/about")
def about():
    return render_template("about.html")




@app.route("/dashboard",methods=['GET','POST'])

def dashboard():


    if 'user' in session and session['user']==params['admin_name']:
        post = Post.query.all()
        return render_template("dashboard.html",post=post)
    if request.method=='POST':
        username=request.form.get('uname')
        userpass = request.form.get('pass')
        if(username==params['admin_name'] and userpass==params['admin_pass']):

            # set the session variavble

            session['user']=username
            post = Post.query.all()

        return render_template("dashboard.html",params=params,post=post)
    return render_template("login.html",param=params)






@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin_name']:
        if request.method=='POST':
            title =request.form.get('title')
            tag=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img=request.form.get('img_file')

        if  sno=="0":
            post=Post(title=title,tline=tag,slug=slug, content=content ,img=img)
            db.session.add(post)
            db.session.commit()
    return render_template('edit.html',params=params)










@app.route("/post/<string:post_slug>",methods=['GET'])
def post(post_slug):
    post=Post.query.filter_by(slug=post_slug).first()
    return render_template("post.html",post=post)




@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user']==params['admin_name']:
        post=Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')






@app.route("/upload",methods=['GET','POST'])
def upload():
    if 'user' in session and session['user']==params['admin_name']:
     if (request.method == 'POST'):
        f=request.files["file1"]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        return "Uploaded Suceesfully"




@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')
app.run(debug=True)







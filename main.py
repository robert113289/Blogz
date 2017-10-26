from flask import Flask,render_template,request,flash,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['DEBUG']=True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:1234@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)

app.secret_key ="pickles"


class Blogs(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.String(255))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,post,owner,pub_date=datetime.utcnow()):
        self.title = title
        self.post = post
        self.pub_date = pub_date
        self.owner = owner

class User(db.Model):
    id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(20),nullable=False)
    blogs = db.relationship('Blogs', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login','validate','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('You must login first')
        return redirect('/login')

@app.route('/')
def index():

    user_id = request.args.get("user")
    user = User.query.filter_by(id=user_id).first()

    if user_id is not None:
        user_id = int(user_id)
        user_blogs = Blogs.query.filter_by(owner_id=user_id)
        return render_template('userblog.html',title="User Blog",user_blogs=user_blogs,user=user)

    if user_id is None:
        user_list = User.query.all()
        return render_template('index.html', user_list=user_list)

    

@app.route('/login', methods=['POST','GET'])
def login():
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password: 
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            flash("You've entered an incorrect password")
            return render_template('login.html',username = username)
        if not user:
            flash("The username you entered is not currently registered")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route("/signup", methods=['POST','GET'])
def validate():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        user = User.query.filter_by(username=username).first()
        
    #username is in the database. redirect to login    
        if user and user.username == username:
            flash('The username you entered already exist. Please Login below.')
            return redirect('/login')
    #username validation
        #username is empty
        if username == "":
            flash("You cannot have an empty username")
            return render_template('signup.html',title="Signup Error",username=username)

        #username is not the right length
        if len(username) < 3 or len(username) > 20:
            flash("Your username has to be atleast 3 characters long but no more than 20")
            return render_template('signup.html',title="Signup Error",username=username)

        #username has a space
        if " " in username:
            flash("You cannot have a space in your username")
            return render_template('signup.html',title="Signup Error",username=username)

    #password validation
        #password is empty
        if password == "":
            flash("You cannot have an empty password")
            return render_template('signup.html',title="Signup Error",username=username)

        #password is not the right length
        if len(password) < 3 or len(password) > 20:
            flash("Your password has to be atleast 3 characters long but no more than 20")
            return render_template('signup.html',title="Signup Error",username=username)

        #password has a space
        if " " in password:
            flash("You cannot have a space in your username")
            return render_template('signup.html',title="Signup Error",username=username)

        #passwords do not match
        if password != password2:
            flash("Your passwords do not match")
            return render_template('signup.html',title="Signup Error",username=username)
        
        #successfull username and password creation
        else:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template("signup.html")


@app.route('/blog', methods=['POST','GET'])
def blog():
    id = request.args.get("id")

    if id is not None:
        id = int(id)
        blog = Blogs.query.filter_by(id=id).first()
        return render_template('singlepost.html',title="Blog",blog=blog)

    if id is None:
        blog_posts = Blogs.query.order_by(Blogs.pub_date.desc())
        return render_template('blog.html',title="Blog",blog_posts=blog_posts)

@app.route('/newpost', methods=['POST','GET'])
def new_post():
        
        
    if request.method == 'POST':
        title= request.form['new_blog_entry_title']
        post= request.form['new_blog_entry']
        owner = User.query.filter_by(username=session['username']).first()
        if title == "":
            flash("You must enter a title for your blog.")
            return render_template('newpost.html',new_blog_entry=post)
            
        if post == "":
            flash("You must add content for your new blog entry")
            return render_template('newpost.html',new_blog_entry_title= title)
            
        
        new_blog_entry = Blogs(title,post,owner)
        db.session.add(new_blog_entry)
        db.session.commit()
        id = new_blog_entry.id
        id = str(id)
        blog = Blogs.query.filter_by(id=id).first()
        return redirect('/blog?id=' + id)

        

    return render_template('newpost.html',title="New Post")

@app.route('/logout')
def logout():

    del session['username']
    flash('You have been logged out')
    return render_template('blog.html')


if __name__ == '__main__':
    app.run()

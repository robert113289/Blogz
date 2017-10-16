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
        



@app.route('/blog')
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

if __name__ == '__main__':
    app.run()

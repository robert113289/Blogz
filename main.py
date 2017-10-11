from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)


class Blogs(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.String(255))

    def __init__(self,title,post):
        self.title = title
        self.post = post

@app.route('/blog')
def blog():



    blog_posts = Blogs.query.all()
    print("*******************************",blog_posts)


    
    return render_template('blog.html',title="Blog",blog_posts=blog_posts)

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    
    
    if request.method == 'POST':
        title= request.form['new_blog_entry_title']
        post= request.form['new_blog_entry']

        new_blog_entry = Blogs(title,post)
        db.session.add(new_blog_entry)
        db.session.commit()
        return render_template('blog.html')

    

    return render_template('newpost.html',title="New Post")

if __name__ == '__main__':
    app.run()

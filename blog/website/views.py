import base64
from io import BytesIO

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .models import Post, User, Comment, Like, Admin_user
from . import db
from base64 import b64encode
import base64
views = Blueprint("views", __name__)


@views.route("/home")
def home():
    posts = Post.query.all()
    user = current_user
    if user:
        image = b64encode(user.user_img).decode("utf-8")
        return render_template("home.html", user=current_user, imag=image, posts=posts)
    else:
        return render_template("home.html", user=current_user,  posts=posts)


@views.route("/")
def not_login():
    posts = Post.query.all()
    return render_template("home.html", user=current_user,  posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('desc')
        text = request.form.get('text')
        img = request.files['image']
        j = img.read()

        if not text:
            flash('Info section cannot be empty', category='success')
        else:
            post = Post(text=text, title=title,
                        description=description, author=current_user.id, post_img=j)

            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='error')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    admin_user = Admin_user.query.filter_by(email=current_user.email).first()
    if not post:
        flash("Post does not exist.", category='error')
    elif admin_user:
        db.session.delete(post)
        db.session.commit()
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/view_post")
@views.route("/view_post/<title>")
@login_required
def view_post(title):
    titl = title.replace("%20", " ")
    post = Post.query.filter_by(title=titl).first()

    image = b64encode(post.post_img).decode("utf-8")
    if not post:
        flash("Post does not exist.", category='error')

    else:
        return render_template("view_post.html", post=post, user=current_user, post_img=image, admin="admin")


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('cmmt')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()

        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    admin_user = Admin_user.query.filter_by(id=current_user.id).first()
    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    elif admin_user:
        db.session.delete(comment)
        db.session.commit()
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['GET'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return "hey its a error"
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('views.home'))


# @views.route("/fav/<post_id>", methods=['GET'])
# @login_required
# def fav(post_id):
#     post = Post.query.filter_by(id=post_id).first()
#     user = User.query.filter_by(id=current_user.id)
#     if user:
#         fav_pos = Fav(user_id=current_user.id, post_id=post.id)
#         db.session.add(fav_pos)
#         db.session.commit()
#     elif post:
#         fav_pos = Fav(user_id=current_user.id, post_id=post.id)
#         db.session.delete(fav_pos)
#         db.session.commit()
#     return redirect(url_for('views.home'))


# @views.route("view_fav/<username>", methods=["GET"])
# @login_required
# def view_fav(username):

#     fav = Fav.query.all()
#     post = Post.query.all()
#     if fav:

#         return render_template('fav.html', fav_post=fav, post=post)

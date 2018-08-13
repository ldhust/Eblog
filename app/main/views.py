#! -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, abort, flash, \
    current_app, make_response
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..models import Role, User, Permission, Post, Comment, Category, Like
from ..import db
from ..decorators import permission_required, admin_required
from flask.ext.sqlalchemy import get_debug_queries

@main.route('/', methods = ['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type = int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
        posts_amount = (current_user.followed_posts.order_by(Post.timestamp.desc()).count(), \
                        Post.query.order_by(Post.timestamp.desc()).count())
    else:
        posts_amount = Post.query.order_by(Post.timestamp.desc()).count()
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)
    posts = pagination.items
    return render_template('index.html', posts = posts, 
                           show_followed = show_followed, pagination = pagination, 
                           posts_amount = posts_amount, redir = '.index', page = page)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user = user, posts = posts, redir = '.user') 
    
@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)    
    page = request.args.get('page', 1, type = int)
    if page <= 0:
        page = (category.posts.count() - 1) / \
                current_app.config['FLASKY_POSTS_PER_PAGE'] + 1    
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False)    
    posts = pagination.items
    return render_template('category.html', category = category, 
                            posts = posts, pagination = pagination, redir = '.category', page = page)

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'你的个人资料已更新')
        return redirect(url_for('.user', username = current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)

@main.route('/new-article', methods = ['GET', 'POST'])
@login_required
def new_article():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(title = form.title.data, category = Category.query.get(form.category.data), 
                    body = form.body.data, author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash(u'文章已发布')
        return redirect(url_for('.post', id = post.id))
    return render_template('new_article.html', form = form)

@main.route('/edit-profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        print 'Role.query.get(form.role.data) = ', Role.query.get(form.role.data)
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(u'资料已更新')
        return redirect(url_for('.user', username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form = form, user = user)
    
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body = form.body.data,
                          post = post,
                          author = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash(u'你的评论已发布')
        return redirect(url_for('.post', id = post.id, page = -1))
    page = request.args.get('page', 1, type = int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out = False) 
    comments = pagination.items
    return render_template('post.html', post = post, form = form,
                           comments = comments, pagination = pagination, redir = '.post')                                         

@main.route('/post/delete/<int:id>')
@login_required
def post_delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        about(403)
    post.delete()
    flash(u'文章已删除')
    return redirect(url_for('.index'))

@main.route('/post/like/<int:id>/<redir>')
@login_required
def post_like(id, redir):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type = int)
    if current_user.is_like_post(post):
        like = Like.query.filter_by(post_id = post.id).first()
        db.session.delete(like)
    else:
        like = Like(post = post, author = current_user._get_current_object())
        db.session.add(like)
    db.session.commit()
    redir_frament = ''.join(('post', str(post.id)))
    if redir == '.index':
        return redirect(url_for('.index', page = page, _anchor=redir_frament))
    elif redir == '.post':
        return redirect(url_for('.post', id = post.id))
    elif redir == '.category':
        return redirect(url_for('.category', page = page, id = post.category.id, _anchor=redir_frament))
    elif redir == '.user':
        return redirect(url_for('.user', username = current_user._get_current_object().username, _anchor=redir_frament))

@main.route('/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        about(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash(u'文章已更新')
        return redirect(url_for('.post', id = post.id))
    form.title.data = post.title
    form.category.data = post.category_id
    form.body.data = post.body
    return render_template('edit_post.html', form = form)
    
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash(u'用户未注册')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注这个用户')
        return redirect(url_for('.user', username = username))
    current_user.follow(user)
    flash(u'你已经关注 %s' % username)
    return redirect(url_for('.user', username = username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户未注册')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你已经关注这个用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你已经取消关注 %s' % username)
    return redirect(url_for('.user', username=username))
    
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash(u'用户未注册')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type = int)
    pagination = user.followers.paginate(
        page, per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out = False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user = user, title = u"的关注者",
                           endpoint = '.followers', pagination = pagination, 
                           follows = follows)
                           
@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户未注册')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注的",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)    
                           
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index'))) 
    resp.set_cookie('show_followed', '', max_age = 30 * 24 * 60 * 60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age = 30 * 24 * 60 * 60)
    return resp 

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type = int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out = False)
    comments = pagination.items
    return render_template('moderate.html', comments = comments,
                           pagination = pagination, page = page) 
                           
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page = request.args.get('page', 1, type = int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page = request.args.get('page', 1, type = int)))      

@main.route('/shutdown') 
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown') 
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'        

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % 
                     (query.statement, query.parameters, query.duration, 
                         query.context))
    return response
from data import articles, users, comments
from server import db_session
from sqlalchemy import desc


def ReadingArticle(id_article):
    db_sess = db_session.create_session()
    article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
    article.readings += 1
    user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
    user.reading += 1
    db_sess.commit()


def getArticleOnText(text):
    db_sess = db_session.create_session()
    return db_sess.query(articles.Articles).filter(articles.Articles.name.ilike('%' + text + '%')).order_by(
        desc(articles.Articles.readings)).all()


def deleteNoneArticle():
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.text == None).delete()


def getTopUsers():
    db_sess = db_session.create_session()
    mark_leaders = db_sess.query(users.User).order_by(desc(users.User.mark))[:4]
    reading_leaders = db_sess.query(users.User).order_by(desc(users.User.reading))[:4]
    subscribers_leaders = db_sess.query(users.User).order_by(desc(users.User.subscribers))[:4]
    return {'mark': mark_leaders, 'reading': reading_leaders, 'subscribe': subscribers_leaders}


def addComment():
    comment = comments.Comment(user=current_user.id, text=answer_text, article_id=article_id,
                               created_date=datetime.datetime.now(), answer_on=make_answer)
    db_sess.add(comment)
    db_sess.commit()
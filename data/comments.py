from users import *


class Comments(db_session.SqlAlchemyBase, UserMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    answer_on = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'))
    article = sqlalchemy.orm.relationship('Articles')


class Comment:
    def __init__(self):
        self.db_sess = db_session.create_session()

    def get(self, article_id: Articles.id) -> list:
        return self.db_sess.query(Comment).filter(Comment.article_id == article_id).all()

    def getData(self, all_comments: list) -> dict:
        data = {}
        for comment in all_comments:
            creator = self.db_sess.query(Users).filter(Users.id == comment.user_id).first()
            time = text_delta(datetime.datetime.now() - comment.created_date)
            data[str(comment.id)] = (creator.name, creator.photo, creator.subscribers, time)
        return data

    def addMark(self, comment_id, mark):
        comment = self.db_sess.query(comments.Comment).filter(comments.Comment.id == comment_id).first()
        if f'{current_user.id}' not in session or 'comments' not in session[str(current_user.id)] or str(
                comment_id) not in session[f'{current_user.id}']['comments']:
            comment.mark += mark
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': mark}}
        elif 1 >= int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) >= -1:
            comment.mark += int(mark)
            comment.mark -= int(session[f'{current_user.id}']['comments'][str(comment_id)])
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': mark}}
        elif int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) <= -1 or int(
                session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) >= 1:
            comment.mark -= int(mark)
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': '0'}}
        self.db_sess.commit()

    def add(self, text, article_id, answer_on):
        comment = comments.Comment(user=current_user.id, text=text, article_id=article_id,
                                   created_date=datetime.datetime.now(), answer_on=answer_on)
        self.db_sess.add(comment)
        self.db_sess.commit()

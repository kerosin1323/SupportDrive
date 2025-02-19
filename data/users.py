from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import *
from articles import *
from forms.UserForm import *


class Users(db_session.SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    marked_articles = sqlalchemy.Column(sqlalchemy.String, default='{}')
    subscribed = sqlalchemy.Column(sqlalchemy.String, default='{}')
    reading = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    description = sqlalchemy.Column(sqlalchemy.String, default='')
    contacts = sqlalchemy.Column(sqlalchemy.String, default='')
    subscribers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    articles = sqlalchemy.orm.relationship("Articles", back_populates='user')
    photo = sqlalchemy.Column(sqlalchemy.String, default='default_logo.jpg')

    def set_password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)


class User:
    def __init__(self):
        self.db_sess = db_session.create_session()

    def create(self, form: RegisterForm) -> None:
        user = Users(name=form.username.data, login=form.login.data)
        user.set_password(form.password.data)
        self.db_sess.add(user)
        self.db_sess.commit()
        login_user(user)

    def addData(self, form: DescriptionProfile, user_id: Users.id) -> None:
        user = self.get(user_id)
        user.name = form.name.data
        photo = form.photo.data
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.photo = filename
        user.description = form.description.data
        user.contacts = form.contacts.data
        self.db_sess.commit()

    def get(self, user_id: Users.id) -> Type[Users]:
        return self.db_sess.query(Users).filter(Users.id == user_id).first()

    def alreadyExist(self, login: str) -> bool:
        return bool(len(self.db_sess.query(Users).filter(Users.login == login).all()))

    def checkAndLogin(self, name: str, password: str) -> Response:
        user = self.db_sess.query(Users).filter(Users.name == name).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect("/")

    def getLeaders(self) -> dict:
        mark_leaders = self.db_sess.query(Users).order_by(desc(Users.mark))[:5]
        reading_leaders = self.db_sess.query(Users).order_by(desc(Users.reading))[:5]
        subscribers_leaders = self.db_sess.query(Users).order_by(desc(Users.subscribers))[:5]
        return {'mark': mark_leaders, 'reading': reading_leaders, 'subscribe': subscribers_leaders}

    def getSubscriptions(self, user_id: Users.id) -> list:
        user = self.get(user_id)
        if user.subscribed:
            return [self.get(int(i)) for i, k in json.loads(user.subscribed).items() if k == '1']

    def subscribeOn(self, user_id: Users.id) -> None:
        user = self.get(current_user.id)
        author = self.get(user_id)
        prev_subs = json.loads(user.subscribed)
        if (not prev_subs) or (str(user.id) not in prev_subs) or (prev_subs[str(user.id)] == '0'):
            author.subscribers += 1
            prev_subs[str(user_id)] = '1'
        elif prev_subs[str(user_id)] == '1':
            author.subscribers -= 1
            prev_subs[str(user_id)] = '0'
        user.subscribed = json.dumps(prev_subs)
        self.db_sess.commit()

    def checkSubscribe(self, user_id: Users.id) -> bool:
        user = self.get(user_id)
        if user.subscribed:
            return str(user_id) in [i for i, k in json.loads(user.subscribed).items() if k == '1']

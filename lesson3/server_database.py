from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.config import  SERVER_DATABASE, POOL_RECYCLE

class ServerStorage(object):
    class AllUsers(object):
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.now()

    class ActiveUsers(object):
        def __init__(self, user_id, ip, port):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port


    class LoggingHistory(object):
        def __init__(self, user_id, date, ip, port):
            self.id = None
            self.user_id = user_id
            self.date = date
            self.ip = ip
            self.port = port

    def __init__(self):
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=POOL_RECYCLE)
        self.metadata = MetaData()
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime),
                            )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('Users.id')),
                                   Column('ip', String),
                                   Column('port', Integer),
                                   )

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('Users.id')),
                                   Column('date', DateTime),
                                   Column('ip', String),
                                   Column('port', Integer),
                                   )

        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoggingHistory, user_login_history)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port):
        rez = self.session.query(self.AllUsers).filter_by(name=username)
        if rez.count():
            user = rez.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        active_user = self.ActiveUsers(user.id, ip, port)
        self.session.add(active_user)

        history = self.LoggingHistory(user.id, user.last_login, ip, port)
        self.session.add(history)

        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.ActiveUsers.ip,
            self.ActiveUsers.port
        ).join(self.AllUsers)
        return query.all()

    def user_logout(self, ip, port):
        self.session.query(self.ActiveUsers).filter_by(ip=ip).filter_by(port=port).delete()
        self.session.commit()

    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoggingHistory.date,
                                   self.LoggingHistory.ip,
                                   self.LoggingHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter_by(name=username)
        return query.all()

if __name__ == '__main__':
    db = ServerStorage()
    db.user_login('client1', '192.168.16.255', '8888')
    db.user_login('client2', '192.168.17.255', '9999')
    print('active users')
    print(db.active_users_list())
    print('\n')
    db.user_logout('192.168.16.255', '8888')
    print('active users')
    print(db.active_users_list())
    print('\n')
    print('All users')
    print(db.users_list())
    print('\n')
    print('login history')
    print(db.login_history('client1'))
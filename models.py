from flask_login import UserMixin

class UserLogin():

    def formDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        self.role = self.__user[3]
        self.avatar = self.__user[4]
        self.login = self.__user[1]
        self.id = self.__user[0]

        return self
    
    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.__user[0])

    
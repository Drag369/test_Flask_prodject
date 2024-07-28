from sqlite3 import*
import base64

class Cars():
    def __init__(self,connection:Connection):
        self.__connect = connection
        self.__cursor = Cursor(connection)
        self.__cursor.row_factory = Row


    def get_allCars(self): 
        
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, brands.brand, cars.img FROM cars INNER JOIN brands ON brands.id = cars.brand_id'
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
            
        except Exception as e:
            print(e)
            return []
        

    def get_carById(self,id:int):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.img, cars.description, brands.brand FROM cars INNER JOIN brands ON brands.id = cars.brand_id WHERE cars.id =?'
        try:
            self.__cursor.execute(sql,(id,))
            return self.__cursor.fetchone()
        except Exception as e:
            print(e)
            return []
        
        

    
    def get_carByName(self,name:str):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, cars.img, brands.brand FROM cars INNER JOIN brands ON brands.id = cars.brand_id WHERE cars.name =?'
        try:
            self.__cursor.execute(sql,(name,))
            return self.__cursor.fetchone()
        except:
            print("ОШИБКА ПОЛУЧЕНИЯ МАШИНЫ ПО НАЗВАНИЮ")
            return []
        
    def get_BrandByName(self,brand:str):
        sql ='SELECT id, brand, description FROM brands WHERE brand = ?'
        try:
            self.__cursor.execute(sql,(brand,))
            return self.__cursor.fetchone()
        except Exception as e:
            print(e)
            return []
        
    
    def get_carByBrand(self,brand:str):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, cars.img, brands.brand FROM cars INNER JOIN brands ON brands.id = cars.brand_id WHERE brands.brand =?'
        try:
            self.__cursor.execute(sql,(brand,))
            return self.__cursor.fetchall()
        except:
            print("ОШИБКА ПОЛУЧЕНИЯ МАШИНЫ ПО БРЕНДУ")
            return []
        

    def add_car(self, name, price, description, brand, img):

        sql = 'INSERT INTO cars (name, price, description, brand_id, img) VALUES (?,?,?, (SELECT id FROM brands WHERE brand = ?),?)'
        try:
            self.__cursor.execute(sql,(name, price, description, brand, img))
            self.__connect.commit()
            return True
        except Exception as e:
            print(e)
            return []
        
    def add_Brand(self, brand, description):
        sql = 'INSERT INTO brands (brand,description) VALUES (?,?)'
        try:
            self.__cursor.execute(sql,(brand,description))
            self.__connect.commit()
            return True
        except:
            print("ОШИБКА ДОБАВЛЕНИЯ БРЕНДА")
            return []
        

    def get_all_Brand(self):
        sql = 'SELECT * FROM brands'
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
        except:
            print("ОШИБКА ПОЛУЧЕНИЯ ВСЕХ БРЕНДОВ")
            return []
        
    def get_random_Car(self, number):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, brands.brand, cars.img FROM cars INNER JOIN brands ON brands.id = cars.brand_id ORDER BY RANDOM() LIMIT  ?'
        try:
            self.__cursor.execute(sql,(number,))
            return self.__cursor.fetchall()
        except:
            print("ОШИБКА ПОЛУЧЕНИЯ РАНДОМНОЙ МАШИНЫ")
            return []
        

    def delete_car(self, id):
        sql = 'DELETE FROM cars WHERE id =?'
        try:
            self.__cursor.execute(sql,(id,))
            self.__connect.commit()
            return True
        except:
            print("ОШИБКА УДАЛЕНИЯ МАШИНЫ")
            return [] 
          
    def delete_Brand(self, id):
        sql = 'DELETE FROM brands WHERE id =?'
        try:
            self.__cursor.execute(sql,(id,))
            self.__connect.commit()
            return True
        except:
            print("ОШИБКА УДАЛЕНИЯ БРЭНДА")
            return []  

   
       

    def sorted_car_priceASC(self):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, brands.brand, cars.img FROM cars INNER JOIN brands ON brands.id = cars.brand_id ORDER BY cars.price ASC'
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
        except:
            print("Ошибка получения списка машин по возрастанию цены")
            return []

    def sorted_car_priceDESC(self):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, brands.brand, cars.img FROM cars INNER JOIN brands ON brands.id = cars.brand_id ORDER BY cars.price DESC'
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
        except:
            print("Ошибка получения списка машин по убыванию цены!")
            return []
        

    def sorted_car_name(self):
        sql = 'SELECT cars.id, cars.name, cars.price, cars.description, brands.brand, cars.img FROM cars INNER JOIN brands ON brands.id = cars.brand_id ORDER BY cars.name ASC'
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
        except:
            print("Ошибка получения списка машин по имени")
            return []

class UserDB:
    def __init__(self, connection: Connection):
        self.__connect = connection
        self.__cursor = Cursor(connection)
        # self.__cursor.row_factory = Row

    def registration(self, login, password):

        sql = "INSERT INTO users (login, password) VALUES (?, ?)"
        try:
            self.__cursor.execute(sql, (login, password))
            self.__connect.commit()
            return self.__cursor.lastrowid
        except:
            print("Ошибка добавления данных в базу данных")
            return 0
        
    def loginUser(self, login):

        try:
            sql = "SELECT * FROM users WHERE login = ?"

            self.__cursor.execute(sql, (login,))
            res = self.__cursor.fetchone()

            if not  res:
                print('Пользователь не найден')
                return False
            
            return res

        except Error as e:
            print('Ошибка получения данных из базы данных', +str(e))

        return False


    
    def getUser(self, user_id):


        try:
            sql = "SELECT * FROM users WHERE id = ? Limit 1"

            self.__cursor.execute(sql, (user_id,))
            res = self.__cursor.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            
            return res

        except Error as e:
            print('Ошибка получения данных из базы данных', +str(e))

        return False
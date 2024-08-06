from flask import Flask, render_template, g, redirect, url_for, request, session, make_response
from sqlite3 import connect, Connection, Cursor
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import DB
import forms
import os



from models import UserLogin



app = Flask(__name__)
app.config['DATABASE'] = 'static/db/database.db'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER_CAR'] = 'static/image/products'

MAX_CONTENT_LENGTH = 1024 * 1024


def connect_db(): 
   
   con = connect(app.config['DATABASE'])
   return con


def get_connect():
    if not hasattr(g, 'link_db'):
      g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
   if hasattr(g, 'link_db'):
    g.link_db.close()

listMenu = [
   {'link':'/index/', 'name':'Главная'},
   {'link':'/all-products/', 'name':'Вся продукция'}

]

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().formDB(user_id, DB.UserDB(get_connect()))

def list_brand():
    objects = DB.Cars(get_connect())
    lst = objects.get_all_Brand()
    return lst



def profile():
    username = (current_user.login,current_user.role,current_user.avatar) if current_user.is_authenticated else ' '
    return username


# передаю необходимое в шаблон html 
@app.context_processor
def base():

    name = profile()
    return dict(name=name)


@app.route('/')
@app.route('/index/')
def index():
    objects = DB.Cars(get_connect())
    lst = objects.get_random_Car(8)
    # print(lst[0][4])
    return render_template('index.html', carsList = lst, brands = list_brand())


# Попробовать вывести в отдельный файл + написать унивирсальную сортировку. 
def sortCar(objects,sort_by):

    if sort_by == "price_asc":
        return objects.sorted_car_priceASC()

    elif sort_by == "price_desc":
        return objects.sorted_car_priceDESC()

    elif sort_by == "name_asc":
        return objects.sorted_car_name()
    
    else:
        return objects.get_allCars()



@app.route('/all-products/')
def allProducts():
    objects = DB.Cars(get_connect())
    sort_by = request.args.get('sort_by')
    lst = sortCar(objects, sort_by)
    brands = objects.get_all_Brand()


    return render_template('allProducts.html', carsList = lst, brands = brands)


@app.route("/car/<name>", methods=['POST','GET'])
def car(name):
    objects = DB.Cars(get_connect())
    lst = objects.get_carByName(name)

    if request.method == 'POST':
        if 'add_basket' in request.form:
            obj = DB.Cars(get_connect())
            obj.add_product_basket(current_user.id, lst[0])



    return render_template('car.html', carsList=lst, brands = list_brand())

@app.route("/basket/", methods=['POST','GET'])
@login_required
def basket():

    objects = DB.Cars(get_connect())
    lst = objects.get_products_basket(current_user.id)
    total_sum = sum(item[1] * item[4] for item in lst)


    
    if request.method == 'POST':
        if 'delete_basket_item' in request.form:
            id_product = request.form['basket_id']
            objects.delete_product_basket(id_product)
            return redirect('/basket/')

    return render_template('basket.html', products = lst ,  name = profile(), total_sum=total_sum)





@app.route("/admin-panel/", methods=['POST','GET'])
@login_required
def add():
    if current_user.role == 'admin':

        objects = DB.Cars(get_connect())

        formCar = forms.addCar()
        formBrand = forms.addBrand()
        allCars = objects.get_allCars()
        all_Brand = objects.get_all_Brand()

        if request.method == 'POST':
            if 'submit_car' in request.form:
                if formCar.validate_on_submit():

                    name=formCar.name.data
                    price=formCar.price.data
                    descriptionCar=formCar.descriptionCar.data
                    brandCar=formCar.brandCar.data
                    images=formCar.images.data

                    # Имя для папки
                    folder_name = name.replace(' ', '_')
                    folder_path = os.path.join(app.config['UPLOAD_FOLDER_CAR'], folder_name)
                    # Создание новой папки для автомобиля
                    os.makedirs(folder_path, exist_ok=True)

                    # Сохранение файла с оригинальным именем в новую папку
                    for image in images:
                        if image and image.filename:
                            filename = secure_filename(image.filename)
                            image_path = os.path.join(folder_path, filename)
                            image.save(image_path)

                    objects.add_car(name, price, descriptionCar,brandCar, folder_name)
                    print("Added car")
                    return redirect('/admin-panel/')    
            elif 'submit_brand' in request.form:
                if formBrand.validate_on_submit():
                    objects.add_Brand(formBrand.brand.data, formBrand.descriptionBrand.data)
                
                    return redirect('/admin-panel/')
            elif 'delete_car' in request.form:
                car_id = request.form['car_id']
                objects.delete_car(car_id)
                return redirect('/admin-panel/')
            
            elif 'delete_brand' in request.form:
                car_id = request.form['car_id']
                objects.delete_Brand(car_id)
                return redirect('/admin-panel/')            
            
            
        
        return render_template('adminPanel.html', formCar=formCar, formBrand=formBrand, brands = list_brand(), allCars = allCars, all_Brand=all_Brand)
    else:
        return "ты не админ!!!"




@app.route('/brand-car/<brand>')
def brandCar(brand):
   objects = DB.Cars(get_connect())
   lst = objects.get_carByBrand(brand)
   Brand = objects.get_BrandByName(brand)

   return render_template('brandCar.html', carsList=lst, brands = list_brand(), brand=Brand)


@app.route("/login/", methods=['POST','GET'])
def login():
    form = forms.Authorization()

    log = form.login.data
    passw = form.password.data
    Object = DB.UserDB(get_connect())

    u = Object.loginUser(log)
    if u and check_password_hash(u[2], passw):
        userlogin = UserLogin().create(u)
        login_user(userlogin)
        return redirect('/')


    return render_template('login.html', form=form,  brands = list_brand())


@app.route("/register/", methods=['POST','GET'])
def register():
    form = forms.Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        Object = DB.UserDB(get_connect())
        Object.registration(form.login.data, hashed_password)
        print('ВОШЕЛ')
        return redirect('/login/')
    return render_template('register.html', form=form,  brands = list_brand())


@app.route("/profile/", methods=['POST','GET'])
def profileUser():

    return render_template('profile.html')



@app.route("/userava")
@login_required
def userava():
    # Получаем бинарные данные изображения из текущего пользователя
    img = current_user.avatar
    
    if not img:
        return "No image available", 404
    
    # Создаем ответ с бинарными данными изображения
    response = make_response(img)
    response.headers['Content-Type'] = 'image/png'  # Убедитесь, что MIME-тип соответствует формату изображения
    
    return response



@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')




app.config['TEMPLATES_AUTO_RELOAD'] = True
if __name__ == "__main__":
    app.run(debug=True)
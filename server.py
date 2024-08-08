from flask import Flask, render_template, g, redirect, url_for, request, session, make_response, flash, send_file
from sqlite3 import connect, Connection, Cursor
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import io
from PIL import Image


import DB
import forms
import os



from models import UserLogin



app = Flask(__name__)
app.config['DATABASE'] = 'static/db/database.db'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER_CAR'] = 'static/image/products'





import logging
from logging.handlers import RotatingFileHandler

log_file_path = os.path.expanduser('~/error.log')

# Настройка обработчика логирования
handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавляем обработчик в логгер приложения
app.logger.addHandler(handler)
app.logger.setLevel(logging.ERROR)

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'An unhandled exception occurred: {e}', exc_info=True)
    return 'Internal Server Error', 500













app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер файла 16 MB

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
    
    return UserLogin().formDB(user_id, DB.UserDB(get_connect()))




def profile():
    username = (current_user.login,current_user.role) if current_user.is_authenticated else ' '
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
    return render_template('index.html', carsList = lst)


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



    return render_template('car.html', carsList=lst)

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

                            img = Image.open(image) # открываю картинку

                            img = img.convert('RGB')
                            
                            img = img.resize((800, 400), Image.LANCZOS)

                            
                            filename = secure_filename(os.path.splitext(image.filename)[0] + '.jpg')
                            image_path = os.path.join(folder_path, filename)

                            img.save(image_path)

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
            
            
        
        return render_template('adminPanel.html', formCar=formCar, formBrand=formBrand, allCars = allCars, all_Brand=all_Brand)
    else:
        return "ты не админ!!!"




@app.route('/brand-car/<brand>')
def brandCar(brand):
   objects = DB.Cars(get_connect())
   lst = objects.get_carByBrand(brand)
   Brand = objects.get_BrandByName(brand)

   return render_template('brandCar.html', carsList=lst, brand=Brand)


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


    return render_template('login.html', form=form)


@app.route("/register/", methods=['POST','GET'])
def register():
    form = forms.Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        Object = DB.UserDB(get_connect())
        Object.registration(form.login.data, hashed_password)
        print('ВОШЕЛ')
        return redirect('/login/')
    return render_template('register.html', form=form )
# ============================



def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/profile/", methods=['POST', 'GET'])
@login_required
def profileUser():
    objects = DB.UserDB(get_connect())
    
    if request.method == 'POST':

        file = request.files['file']


        if file and allowed_file(file.filename):
                # Открытие изображения и изменение его размера
                image = Image.open(file)
                format = image.format  # Сохранение исходного формата изображения

                # Преобразование в RGB для всех форматов, кроме JPEG
                if format != 'JPEG':
                    image = image.convert('RGB')

                # Изменение размера до 100x100 пикселей
                image = image.resize((250, 250), Image.LANCZOS)

                # Сохранение изображения в бинарный поток
                img_io = io.BytesIO()
                image.save(img_io, format=format)  # Сохранение в исходном формате
                img_io.seek(0)  # Вернуть указатель на начало потока

                avatar = img_io.read()  # Преобразование изображения в бинарные данные

                # Сохраняем аватарку
                objects.updateAvatar(current_user.id, avatar)

    return render_template('profile.html', user=objects.getUser(current_user.id))



@app.route("/userava")
def userava():
    objects = DB.UserDB(get_connect())
    user = objects.getUser(current_user.id)
    if user and user[4]:  # Проверяем наличие пользователя и его аватара
        return send_file(io.BytesIO(user[4]), mimetype='image/jpeg', as_attachment=False, download_name='avatar.jpg')
    return redirect(url_for('static', filename='default_avatar.jpg'))



@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')




app.config['TEMPLATES_AUTO_RELOAD'] = True
if __name__ == "__main__":
    app.run()
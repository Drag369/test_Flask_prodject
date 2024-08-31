from flask import Flask, render_template, g, redirect, url_for, request, session, make_response, flash, send_file
from sqlite3 import connect, Connection, Cursor
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import io
from PIL import Image

import requests
import DB
import forms
import os



from models import UserLogin



app = Flask(__name__)

app.config['DATABASE'] = '/home/drago/Документы/project/test_Flask_prodject/static/db/database.db'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER_CAR'] = 'static/image/products'


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
    log = forms.Authorization()
    reg = forms.Registration()
    name = profile()

    return dict(name=name, reg = reg, log=log)


@app.route('/')
@app.route('/index/')
def index():

    api_url = 'http://127.0.0.1:8000/api/v1/cars/random?count=8' # Работает вывод рандомных записеей мпшин 
    response = requests.get(api_url)
    data = response.json()
    
    return render_template('index.html', carsList= data["items"])





@app.route('/all-products/')
def allProducts():
    sort_by = request.args.get('sort_by')
    if sort_by == "price_asc":
        api_url = 'http://127.0.0.1:8000/api/v1/cars/?sort_by=asc' # Сортировка по цене по убыванию
    elif sort_by == "price_desc":
        api_url = 'http://127.0.0.1:8000/api/v1/cars/?sort_by=desc' # Сортировка по цене по возрастанию
    else:
        api_url = 'http://127.0.0.1:8000/api/v1/cars/' # Без сортировки

    response = requests.get(api_url)
    data = response.json()

    ap_url = 'http://127.0.0.1:8000/api/v1/brands/' # Вывод брендов
    resp= requests.get(ap_url)
    da = resp.json()

    return render_template('allProducts.html', carsList= data["items"], brands=da['items'])


@app.route("/car/<name>", methods=['POST','GET'])
def car(name):

    api_url = f'http://127.0.0.1:8000/api/v1/cars/name?name={name}'
    response = requests.get(api_url)
    data = response.json()                                         #Корзину позже

    return render_template('car.html', carsList=data)

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
    api_url = f'http://127.0.0.1:8000/api/v1/brands/{brand}'
    response = requests.get(api_url)
    data = response.json()


    ap_url = f'http://127.0.0.1:8000/api/v1/cars/brancar?brand={brand}' # вывод инфы о бренде и его страница + машины этого бренда
    resp = requests.get(ap_url)
    da = resp.json()
    return render_template('brandCar.html', carsList=da['items'], brand=data)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = forms.Authorization()
    if request.method == 'POST' and form.validate_on_submit():
        log = form.login.data
        passw = form.password.data
        Object = DB.UserDB(get_connect())
        u = Object.loginUser(log)
        if u and check_password_hash(u[2], passw):
            userlogin = UserLogin().create(u)
            
            login_user(userlogin)
            return redirect('/')



@app.route("/register/", methods=['POST','GET'])
def register():
    form = forms.Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        Object = DB.UserDB(get_connect())
        Object.registration(form.login.data, hashed_password)
        print('ВОШЕЛ')
        return redirect('/')

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
        print(user[4])
        return send_file(io.BytesIO(user[4]), mimetype='image/jpeg', as_attachment=False, download_name='avatar.jpg')
    return redirect(url_for('static', filename='default_avatar.jpg'))



@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')


app.config['TEMPLATES_AUTO_RELOAD'] = True
if __name__ == "__main__":
    # import logging



    # # Настройка логирования
    # log_filename = 'app_errors.log'
    # logging.basicConfig(
    #     filename=log_filename,
    #     level=logging.ERROR,
    #     format='%(asctime)s %(levelname)s: %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )


    app.run(debug=True)
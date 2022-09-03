from flask import Flask , render_template , request ,redirect ,url_for ,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from flask_wtf.csrf import CSRFProtect
from flask.helpers import flash
from flask_login import LoginManager ,UserMixin ,login_user , logout_user ,current_user
from enum import Enum as userEnum
from flask_admin import BaseView, expose

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql+mysqldb://root:123123@127.0.0.1/sinhvien'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login = LoginManager(app)

app.config['SECRET_KEY'] = '12345678'
class sinhvien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100))
    masosv = db.Column(db.Integer)
    email = db.Column(db.String(100))



class quyenUser(userEnum):
    admin=1
    user=2

class taikhoan2(db.Model,UserMixin):


    id = db.Column(db.Integer, primary_key=True)
    taikhoan = db.Column(db.String(100))
    matkhau = db.Column(db.String(100))
    quyen = db.Column(Enum(quyenUser), default = quyenUser.user)

    def __init__(self,taikhoan,matkhau,quyen):
        self.taikhoan = taikhoan
        self.matkhau = matkhau
        self.quyen = quyen
    def __repr__(self) -> str:
        return f'<User {self.taikhoan}>'


@app.before_first_request
def create_table():
    db.create_all()



@login.user_loader
def load_user(user_id):
    return taikhoan2.query.get(user_id)

@app.route("/dangxuat")
def dangxuat123():
    logout_user()
    return redirect("/")


@app.route("/dangki" , methods = ['GET','POST'])
def dangki():

    if request.method == 'GET':
        return render_template("dangki.html")
    if request.method == 'POST':
        taikhoan = request.form['tendangnhap']
        matkhau = request.form['matkhautaikhoan']
        quyen = request.form['quyen']
        themvodb = taikhoan2(taikhoan=taikhoan, matkhau=matkhau,quyen=quyen)
        db.session.add(themvodb)
        db.session.commit()
        return redirect("/")

@app.route("/" , methods = ['GET','POST'])
def dangnhap():

    return render_template("dangnhap.html")


#





@app.route("/xacminhdangnhap" , methods = ['GET','POST'])
def xacminhdangnhap():
    if request.method == 'POST':
        ten = request.form['tendangnhap']
        matkhau = request.form['matkhautaikhoan']
        xacminh = taikhoan2.query.filter(taikhoan2.taikhoan == ten,
                                        taikhoan2.matkhau == matkhau).first()
        if xacminh :
            login_user(user=xacminh)
            if current_user.is_authenticated and current_user.quyen == quyenUser.admin :
                quyentk = 1
            else:
                quyentk = 2
            return render_template("dangnhap.html" , quyentk = quyentk)
        else :
            return redirect("/create")


@app.route("/read")
def hello_world():
    data = sinhvien.query.all()
    return render_template("read.html",data2 = data)

@app.route("/create" , methods = ['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template("create.html")

    if request.method == 'POST':
        ten = request.form['ten']
        email = request.form['email']
        masosv = request.form['maso']
        themvodb = sinhvien(ten=ten, email=email, masosv=masosv)
        db.session.add(themvodb)
        db.session.commit()
        return redirect("/read")




@app.route("/delete", methods = ['GET','POST'])
def delete():
    if request.method == 'GET':
        return render_template("delete.html")
    if request.method == 'POST':
        ten = request.form['xoa']
        sinhvien.query.filter_by(ten=ten).delete()
        db.session.commit()
        return redirect("/")




@app.route("/update", methods = ['GET','POST'])
@csrf.exempt
def update():
    if request.method == 'GET':
        return render_template("update.html")
    if request.method == 'POST':
        email = request.form["caimuondoi"]
        emailsauthaydoi = request.form["doithanh"]
        found_email = sinhvien.query.filter_by(email=email).first()
        found_email.email = emailsauthaydoi
        db.session.commit()
        return redirect("/")

@app.route('/doidata', methods=['POST'])
@csrf.exempt
def thaydoi():
    input_json = request.get_json(force=True)
    email = input_json['email']
    emailsauthaydoi = input_json['emailsaudoi']
    thanhcong = None
    if sinhvien.query.filter_by(email=email).first() is not None:
        data = sinhvien.query.filter_by(email=email).first()
        data.email = emailsauthaydoi
        db.session.commit()
        thanhcong = True
        return jsonify({'thay doi thanh cong': thanhcong})
    else:
        thanhcong = False
        return jsonify({'thay doi thanh cong': thanhcong})
    #data.email = emailsauthaydoi
    #db.session.commit()
    #return jsonify({'thanhcong': True},)
    return



if __name__ == "__main__" :
    db.create_all()
    app.run(debug=True)
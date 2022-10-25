from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#Initialise app + bootstrap
app = Flask(__name__)
Bootstrap(app)

#Configuration for MySQL
app.config['SECRET_KEY'] = 'eecb95b8426343160802cb1d3d8c592492c4cd02d4084dbf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c1997660:Baxter2427@csmysql.cs.cf.ac.uk:3306/c1997660_flaskdiary'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


from diary import routes

#Admin Views
from flask_admin import Admin
from diary.views import AdminView
from diary.models import User, Entry, Project
admin = Admin(app,name='Admin panel', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Entry, db.session))
admin.add_view(AdminView(Project, db.session))

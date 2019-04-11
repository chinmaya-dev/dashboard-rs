from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from config import Config, ProductionConfig
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
moment = Moment()
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'







def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)




    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)



    from .users import bp as user_bp
    from .posts import bp as post_bp
    from .platform import bp as platform_bp
    from .auth import bp as auth_bp
    from .blog import bp as blog_bp
    from .errors import bp as errors_bp
    from .visualization import bp as visualization_bp
    from .main import bp as main_bp
    from .messages import bp as messages_bp




    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(post_bp, url_prefix='/posts')
    app.register_blueprint(platform_bp, url_prefix='/platform')
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(visualization_bp, url_prefix='/visualization')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(messages_bp, url_prefix='/messages')


    return app

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USE_AUTHENTICATION = True
    MAIL_USERNAME = 'quantamixsolutions@gmail.com'
    MAIL_PASSWORD = 'ylblvxsrstdswbvj'
    FLASKY_MAIL_SENDER = 'Flasky Admin <quantamixsolutions@gmail.com>'
    FLASKY_ADMIN = 'asjs0688@gmail.com'
    FLASKY_MAIL_SUBJECT_PREFIX = 'TTB WEB live erros'
    SSL_REDIRECT = False
    LOG_TO_STDOUT = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_COMMENTS_PER_PAGE = 30
    ELASTICSEARCH_URL= 'http://localhost:9200'
    FACEBOOK_APP_ID = '268153730556085'
    FACEBOOK_APP_SECRET = '39b862676dd7c85e2ee5d6d5fde8ae36'
    RECAPTCHA_PUBLIC_KEY = '6LdTGH0UAAAAAN4NdKpYagPrXVOazH9JIHvF64Vw'
    RECAPTCHA_PRIVATE_KEY = '6LdTGH0UAAAAAA3WFfNgtDVM7zv9T1oajlt4f6kU'
    POSTS_PER_PAGE = 25

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'


class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

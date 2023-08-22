class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@localhost/music_library'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

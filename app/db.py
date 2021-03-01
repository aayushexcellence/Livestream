from flask_pymongo import PyMongo


def init_db():
    mongo = PyMongo()
    return mongo


def get_db(app, mongo):
    app.config["MONGO_URI"] = "mongodb+srv://root:9KuAMuv8807YP8wH@cluster0.v8o7t.mongodb.net/platoo?retryWrites=true&w=majority"#"mongodb+srv://xmage:xmage@cluster0-xooqb.mongodb.net/test?retryWrites=true"
    mongo.init_app(app)

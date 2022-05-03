from GreenPy.app import config_app

#Run en phase production
if __name__ == "__main__":
    app = config_app("production")
    app.run(debug=True)
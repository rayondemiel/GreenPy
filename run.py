from flask import Flask

app = Flask("Application")

@app.route("/")
def accueil():
    return "Welcome to GreenPy project !"

@app.route("/militant/<int:militant_id>")
def militant(militant_id):
    return "On est sur le militant numéro " + str(militant_id)

@app.route("/projet_contesté/<int:objContest_id>")
def objContest(objContest_id):
    return "On est sur le projet numéro " + str(objContest_id)

if __name__ == "__main__":
    app.run()
from flask import Flask, redirect, render_template, url_for


@app.route("/login", methods=['POST', 'GET'])
def login():
    if form.method == "POST":
        username = form['username']
        password = form['password']
        return redirect(url_for('home'))
    else:
        return render_template("login.html", title="Login")
        

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if form.method == "POST":
        username = form['username']
        password = form['password']
        password2 = form['password2']
        
        return redirect(url_for("login"))
    else:
        return render_template("signup.html", title="Signup")



@app.route("/")
def home():
    return render_template("index.html", title="HomePage")


@app.route(404)
def unkown():
    return url_for('home')


with app.app_context:
    if __name__ == "__name__":
        db.create_all()
        app.run(debug=True)

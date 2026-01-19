from flask import Flask, flash, redirect, url_for, render_template, make_response, request, session
import requests, json
from datetime import datetime, timedelta

API_URL = "http://localhost:5555"
app = Flask(__name__)
app.secret_key = "cefc5e94-190a-47dd-8740-838b48223bd1"

# Index
@app.route("/")
def home():
    return redirect(url_for("leaderboard"))

@app.route("/leaderboard/", methods=["POST", "GET"])
def leaderboard():
    # When the website's form is submitted
    if(request.method == "POST"):
        # When button Log is pressed
        if(request.form['btn_identifier'] == "Log"):
            r = requests.post(API_URL + "/request_match", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "opponent": request.form["un"],
                "result": request.form["rs"]
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('leaderboard'))
            return redirect(url_for("leaderboard"))
        # When button Matchmaking is pressed
        elif(request.form['btn_identifier'] == "Matchmaking"):
            r = requests.get(API_URL + "/matchmaking", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"]
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('leaderboard'))
            d = json.loads(r.text)
            opponent = d["username"]
            return redirect(url_for("leaderboard") + "?opp=" + opponent)
        # When button Accept is pressed
        elif(request.form['btn_identifier'] == "Accept"):
            print("OK")
            r = requests.post(API_URL + "/accept_match_request", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "match_request_id": request.form['match_request_id']
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('leaderboard'))
            return redirect(url_for("leaderboard"))
        # When button Reject is pressed
        elif(request.form['btn_identifier'] == "Reject"):
            r = requests.post(API_URL + "/reject_match_request", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "match_request_id": request.form['match_request_id']
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('leaderboard'))
            return redirect(url_for("leaderboard"))
        # When button Sort is pressed
        elif(request.form['btn_identifier'] == "Sort"):
            # Redirect with the sort type as a url argument
            return redirect(url_for("leaderboard")+ "?sort=" + request.form['st'])
    # When the website is accessed
    elif(request.method == "GET"):
        # Check if the user is logged in
        if((not "NAISCHESS_TOKEN" in session) or (not "NAISCHESS_USERNAME" in session)):
            return redirect(url_for("login"))
        # Create a dictionary to store the credentials
        credentials = {"password": session["NAISCHESS_TOKEN"], "username": session["NAISCHESS_USERNAME"]}
        # Request the api for user data
        r = requests.get(API_URL + "/check_session", json=credentials)
        # Check if user's login credentials are correct
        if (not r.ok):
            return redirect(url_for("login"))
        # Save the user data as a python variable
        user = json.loads(r.text)
        # Request the api for all users data
        r = requests.get(API_URL + "/users", json=credentials)
        if(not r.ok):
            d = json.loads(r.text)
            error = d["error"]
            flash(error)
            return redirect(url_for('leaderboard'))
        
        # Save all users data as a python variable
        users = json.loads(r.text)
        
        sort_type = request.args.get("sort", default="")

        # Sorting
        length = len(users)
        if(sort_type == "easc"):
            i=0
            flag=True
            while i < length and flag:
                flag=False
                for j in range(length - 1 - i):
                    if(users[j]["elo"] > users[j+1]["elo"]):
                        temp = users[j+1]
                        users[j+1] = users[j]
                        users[j] = temp
                        flag = True
                i += 1
        elif(sort_type == "edsc"):
            i=0
            flag=True
            while i < length and flag:
                flag=False
                for j in range(length - 1 - i):
                    if(users[j]["elo"] < users[j+1]["elo"]):
                        temp = users[j+1]
                        users[j+1] = users[j]
                        users[j] = temp
                        flag = True
                i += 1
        elif(sort_type == "uasc"):
            i=0
            flag=True
            while i < length and flag:
                flag=False
                for j in range(length - 1 - i):
                    if(users[j]["username"].lower() > users[j+1]["username"].lower()):
                        temp = users[j+1]
                        users[j+1] = users[j]
                        users[j] = temp
                        flag = True
                i += 1
        elif(sort_type == "udsc"):
            i=0
            flag=True
            while i < length and flag:
                flag=False
                for j in range(length - 1 - i):
                    if(users[j]["username"].lower() < users[j+1]["username"].lower()):
                        temp = users[j+1]
                        users[j+1] = users[j]
                        users[j] = temp
                        flag = True
                i += 1
        
        # Request the api for all match requests data related to the user
        r = requests.get(API_URL + "/get_match_request", json=credentials)
        if(not r.ok):
            d = json.loads(r.text)
            error = d["error"]
            flash(error)
            return redirect(url_for('leaderboard'))

        # Save all match requests data related to the user 
        mr = json.loads(r.text).get("match_request", None)
        # Request the api for all matches data related to the user 
        r = requests.get(API_URL + "/get_matches", json=credentials)
        if(not r.ok):
            d = json.loads(r.text)
            error = d["error"]
            flash(error)
            return redirect(url_for('leaderboard'))
        # Save all matches data related to the user 
        matches = reversed(json.loads(r.text))
        
        # Find if there is a matchmaking opponent
        opponent = request.args.get("opp", default="")
        # Pass the variables and render it on a html template
        return render_template("leaderboard.html", users=users, mr=mr, matches=matches, user=user, opponent=opponent, datetime=datetime, timedelta=timedelta)
    

@app.route("/login/", methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        r = requests.post(API_URL + "/login", json={
            "username": request.form["un"],
            "password": request.form["pw"]
        })
        if(not r.ok):
            d = json.loads(r.text)
            error = d["error"]
            return render_template('login.html', error=error)
        d = json.loads(r.text)
        session["NAISCHESS_TOKEN"] = d["password"]
        session["NAISCHESS_USERNAME"] = d["username"]
        return redirect(url_for("leaderboard"))
    elif(request.method == "GET"):
        if("NAISCHESS_TOKEN" in session):
            redirect(url_for("leaderboard"))
        return render_template("login.html", error=None)

@app.route("/signup/", methods=["POST", "GET"])
def signup():
    if(request.method == "POST"):
        if(request.form["pw"] != request.form["pwr"]):
            flash("Re-entered password is incorrect")
            return redirect(url_for('signup'))
        r = requests.post(API_URL + "/signup", json={
            "username": request.form["un"],
            "name": request.form["rn"],
            "password": request.form["pw"]
        })
        if(not r.ok):
            d = json.loads(r.text)
            error = d["error"]
            flash(error)
            return redirect(url_for('signup'))
        d = json.loads(r.text)
        session["NAISCHESS_TOKEN"] = d["password"]
        session["NAISCHESS_USERNAME"] = d["username"]
        return redirect(url_for("leaderboard"))
    else:
        return render_template("signup.html")

@app.route("/logout/")
def logout():
    session.pop("NAISCHESS_TOKEN")
    return redirect(url_for("login"))

@app.route("/admin/", methods=["POST", "GET"])
def admin():
    if(request.method == "POST"):
        # When button Ban is pressed
        if(request.form['btn_identifier'] == "Ban"):
            r = requests.post(API_URL + "/a_ban", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "target_id": request.form["target_id"],
                "ban": True
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin"))
        # When button Unban is pressed
        elif(request.form['btn_identifier'] == "Unban"):
            r = requests.post(API_URL + "/a_ban", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "target_id": request.form["target_id"],
                "ban": False
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin"))
        elif(request.form['btn_identifier'] == "Hide"):
            r = requests.post(API_URL + "/a_hide", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "target_id": request.form["target_id"],
                "hide": True
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin"))
        elif(request.form['btn_identifier'] == "Unhide"):
            r = requests.post(API_URL + "/a_hide", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "target_id": request.form["target_id"],
                "hide": False
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin") + "?inspect=" +  request.args.get("inspect", default=""))
        # When button Accept is pressed
        elif(request.form['btn_identifier'] == "Accept"):
            r = requests.post(API_URL + "/accept_match_request", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "match_request_id": request.form['match_request_id']
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin") + "?inspect=" + request.args.get("inspect", default=""))
        # When button Reject is pressed
        elif(request.form['btn_identifier'] == "Reject"):
            r = requests.post(API_URL + "/reject_match_request", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "match_request_id": request.form['match_request_id']
            })
            if(not r.ok):
                d = json.loads(r.text)
                error = d["error"]
                flash(error)
                return redirect(url_for('admin'))
            return redirect(url_for("admin") + "?inspect=" + request.args.get("inspect", default=""))
        elif(request.form['btn_identifier'] == "Inspect"):
            return redirect(url_for("admin") + "?inspect=" + request.form["target_id"])
    elif(request.method == "GET"):
        # Check if the user is logged in
        if((not "NAISCHESS_TOKEN" in session) or (not "NAISCHESS_USERNAME" in session)):
            return redirect(url_for("login"))
        # Create a dictionary to store the credentials
        credentials = {"password": session["NAISCHESS_TOKEN"], "username": session["NAISCHESS_USERNAME"]}
        # Request the api for user data
        r = requests.get(API_URL + "/check_session", json=credentials)
        # Check if user's login credentials are correct
        if (not r.ok):
            return redirect(url_for("login"))
        # Save the user data as a python variable
        user = json.loads(r.text)
        # Check if the user has the permission to access the admin dashboard
        if (not user["isadmin"]):
            return render_template("admin_blocked.html")
        # Request the api for all users data
        r = requests.get(API_URL + "/a_users", json=credentials)
        if(not r.ok):
            d = json.loads(r.text)
            fetch_error = d["error"]
            return render_template('leaderboard.html', fetch_error=fetch_error)
        # Save all users data as a python variable
        users = json.loads(r.text)
        # Find the specified user from the retrieved match data
        inspect = request.args.get("inspect", default="")
        i_user = None
        if(inspect != ""):
            r = requests.get(API_URL + "/a_inspect", json={
                "password": session["NAISCHESS_TOKEN"],
                "username": session["NAISCHESS_USERNAME"],
                "inspect": inspect
            })
            # Save the inspected users' data as a python variable
            i_user = json.loads(r.text)
        return render_template("admin.html", users=users, i_user=i_user, datetime=datetime, timedelta=timedelta)

if __name__ == "__main__":
    app.run(port=9013, debug=True)
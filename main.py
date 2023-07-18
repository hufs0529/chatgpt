from flask import Flask, render_template, request, session
import openai
import jwt

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

openai.api_key = ""
AUTHORIZED_USERS = set()  # 예시로 사용자 이름을 직접 설정합니다. 실제로는 데이터베이스 또는 사용자 관리 시스템을 사용해야 합니다.

def is_authorized():
    token = session.get("token")
    if not token:
        return False

    try:
        decoded_token = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        username = decoded_token.get("username")
        return username in AUTHORIZED_USERS
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

@app.route("/", methods=["GET", "POST"])
def home():
    if not is_authorized():
        return render_template("login.html")

    if request.method == "POST":
        content = request.form["content"]

        messages = session.get("messages", [])
        messages.append({"role": "user", "content": content})

        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        chat_response = completion.choices[0].message.content

        messages.append({"role": "assistant", "content": chat_response})
        session["messages"] = messages

        return render_template("chat.html", messages=messages)

    return render_template("chat.html", messages=[])

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 실제로는 사용자 정보를 데이터베이스에 저장하거나 사용자 관리 시스템을 사용해야 합니다.

        AUTHORIZED_USERS.add(username)
        session["user"] = username

        return render_template("login.html")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 실제로는 사용자 정보를 데이터베이스에서 확인하거나 사용자 관리 시스템을 사용해야 합니다.

        if username in AUTHORIZED_USERS:
            token = jwt.encode({"username": username}, app.secret_key, algorithm="HS256")
            session["token"] = token
            print(token)
            return render_template("chat.html", messages=[])
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("messages", None)
    session.pop("token", None)
    return render_template("login.html")

if __name__ == "__main__":
    app.run()

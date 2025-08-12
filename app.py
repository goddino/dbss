from flask import Flask, render_template, request
from groq import Groq
import os
import joblib
import requests
import sqlite3
import datetime
from dotenv import load_dotenv

# Load .env variables to the environment.
# Looks for a .env file in the dir of this script or searches for it incrementally higher up.
load_dotenv()

# Get Telegram info from environment variable.
TELEGRAM_BOT_NAME = os.environ.get('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_DOMAIN_URL = os.environ.get('TELEGRAM_DOMAIN_URL')

client = Groq()

app = Flask(__name__)

def get_cursor_rows(c):
    """
    Helper function to fetch all rows from a cursor.
    """
    r=""
    for row in c:
        print(row)
        r = r + str(row) + "\n"

    if r == "":
        r = "No records found."
    return r
@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    # db
    return(render_template("main.html"))
           
@app.route("/spam",methods=["GET","POST"])
def spam():
    return(render_template("spam.html"))
           
@app.route("/spam_pred",methods=["GET","POST"])
def spam_pred():
    q : str
    try:
        q = str(request.form.get("q", "spam"))  # Default to "spam" if "q" not submitted in form.
    except (ValueError, TypeError):
        q = "spam"  # Default value if q was submitted as '' or some invalid value.
    
    # Load models from file.
    model = joblib.load("lr_model.jl")
    cv = joblib.load("cv_model.jl")

    # Make prediction
    q_cv = cv.transform([q])
    pred = model.predict(q_cv)
    r = "No." if pred[0] == "ham" else "Yes!"
        
    return(render_template("spam_pred.html",r=r, q=q))
           
@app.route("/dbs",methods=["GET","POST"])
def dbs():
    return(render_template("dbs.html"))
           
@app.route("/llama",methods=["GET","POST"])
def llama():
    return(render_template("llama.html"))
           
@app.route("/ds",methods=["GET","POST"])
def ds():
    return(render_template("ds.html"))
           
@app.route("/prediction",methods=["GET","POST"])
def prediction():
    q : float
    try:
        q = float(request.form.get("q", 1.35))  # Default to 1.35 if "q" not submitted in form.
    except (ValueError, TypeError):
        q = 1.35  # Default value if q was submitted as '' or some invalid value.
    
    # Load model from file.
    model = joblib.load("dbs.jl")

    # Make prediction
    pred = model.predict([[q]])

    return(render_template("prediction.html",r=pred[0][0], q=q))
           
@app.route("/llama_reply",methods=["GET","POST"])
def llama_reply():
    q = request.form.get("q")

    # load model
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    return(render_template("llama_reply.html",r=completion.choices[0].message.content))

@app.route("/ds_reply",methods=["GET","POST"])
def ds_reply():
    q = request.form.get("q")

    # load model
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    return(render_template("ds_reply.html",r=completion.choices[0].message.content))

@app.route("/telegram",methods=["GET","POST"])
def telegram():
    domain_url = 'https://dbss-issn.onrender.com'
    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={domain_url}/webhook"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = f"The telegram bot is running at t.me/{TELEGRAM_BOT_NAME}."
    else:
        status = "Failed to start the telegram bot at t.me/{TELEGRAM_BOT_NAME}. Please check the logs."
    
    return(render_template("telegram.html", status=status))

@app.route("/webhook",methods=["GET","POST"])
def webhook():

    # This endpoint will be called by Telegram when a new message is received
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        query = update["message"]["text"]
        print(query)

        # Pass the query to the Groq model
        client = Groq()
        completion_ds = client.chat.completions.create(
            # model="deepseek-r1-distill-llama-70b",
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        response_message = completion_ds.choices[0].message.content
        print(response_message)

        # Send the response back to the Telegram chat
        send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_message_url, json={
            "chat_id": chat_id,
            "text": response_message
        })
    return('ok', 200)

@app.route("/stop_telegram",methods=["GET","POST"])
def stop_telegram():
    domain_url = TELEGRAM_DOMAIN_URL
    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    webhook_response = requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = f"The telegram bot (t.me/{TELEGRAM_BOT_NAME}) webhook has stopped."
    else:
        status = "Failed to stop the telegram bot (t.me/{TELEGRAM_BOT_NAME}) webhook. Please check the logs."
    
    return(render_template("stop_telegram.html", status=status))

@app.route("/user_log",methods=["GET","POST"])
def user_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    insert = request.form.get("insert", "false") == "true"
    if insert:
        # Insert new user log into the database
        q = request.form.get("q", "inserted user")
        t = datetime.datetime.now()
        c.execute('INSERT INTO user (name, timestamp) VALUES (?, ?)', (q, t))
        conn.commit()
    # Check remaining records
    c.execute('''select * from user''')
    r = get_cursor_rows(c)
    c.close()
    conn.close()
    return(render_template("user_log.html", r=r))

@app.route("/delete_log",methods=["GET","POST"])
def delete_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    # Delete all records from the user table
    c.execute('DELETE FROM user',);
    conn.commit()
    # Check remaining records
    c.execute('''select * from user''')
    r = get_cursor_rows(c)
    c.close()
    conn.close()
    return(render_template("delete_log.html", r=r))

@app.route("/huggingface",methods=["GET","POST"])
def huggingface():
    return(render_template("huggingface.html"))

if __name__ == "__main__":
    app.run()
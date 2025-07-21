from flask import Flask, render_template, request
from groq import Groq
import os
import joblib
import requests
import pandas as pd
import sklearn

#https://console.groq.com/keys
if os.environ.get('GROQ_API_KEY') == None:
    os.environ['GROQ_API_KEY'] = ""
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if TELEGRAM_BOT_TOKEN == None:
    TELEGRAM_BOT_TOKEN = ""

client = Groq()

app = Flask(__name__)

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
    
    # Load model from file.
    model = joblib.load("lr_model.jl")

    # Make prediction
    pred = model.predict([[q]])
    return(render_template("spam_pred.html",r=pred[0][0], q=q))
           
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
        status = "The telegram bot is running. Please check with the telegram bot. @dsai_xr_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."
    
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
    domain_url = 'https://dbss-issn.onrender.com'
    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    webhook_response = requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot webhook has stopped. @dsai_xr_bot"
    else:
        status = "Failed to stop the telegram bot webhook. Please check the logs."
    
    return(render_template("stop_telegram.html", status=status))

if __name__ == "__main__":
    app.run()
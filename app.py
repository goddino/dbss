from flask import Flask, render_template, request
from groq import Groq
import os
import joblib
import requests

#https://console.groq.com/keys
if os.environ.get('GROQ_API_KEY') == None:
    os.environ['GROQ_API_KEY'] = ""

client = Groq()

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    # db
    return(render_template("main.html"))
           
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
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    if TELEGRAM_BOT_TOKEN == None:
        TELEGRAM_BOT_TOKEN = ""
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

if __name__ == "__main__":
    app.run()
# DBSS Web Application

![Flask](assets/Framework-Flask-blue.svg)
![Python](assets/Python-3.svg)
![Groq](assets/LLM-Groq_API-green.svg)

## Introduction
A multi-functional Flask web application demostrating:
- AI chat services with Telegram bot integration
- Deployment of built AI models for numerical prediction and text classification.
- SQLite usage.
- Embedding of Gradio app deployed on Hugging Face.

## Usage
To use this project, please perform the following in order.
### Prerequisites
1. Clone the repository to your desired deployment site.
   - ```bash
      git clone https://github.com/goddino/dbss.git
      cd dbss
      ```
1. Create the conda environment required using the provided [environment.yml](environment.yml).
   - `conda env create -f environment`
1. Activate the conda environment:
   - `conda activate m5dbss`
1. Provide required parameters in [.env](.env).
    - Create a `.env` file in root directory
    - Copy the contents of [env.txt](env.txt) to `.env`.
    - Provide all the missing values.
    - For the Telegram bot webhook:
      - `TELEGRAM_DOMAIN_URL` must be on a publicly accessible domain where this Flask app will be deployed.

### Deployment
- For local deployment:
  - ```bash
    python app.py
    ```
  - This is fine in general except for the Telegram bot feature.
    - For the bot to have Gen AI response, this App must be hosted on a publicly accessible domain.
- Deployment on [Render.com](https://render.com/):
  - Process:
    - Go to [dashboard](https://dashboard.render.com/).
    - Add new -> Web Service
    - Select the repository in which this code resides in.
    - Add the Environment Variables required for this project.
      - Either:
        - Add from this project's [.env](.env), or:
        - Manually add the [.env](.env) variables one by one.
    - Select the appropriate Instance Type.
      - There is a "Free" instance type.
      - Note that after a period of inactivity, "Free" instances:
        - Would spin down.
        - The next call to the instance would take a while to be executed.
    - Deploy Web Service.
  - When the new Web Service is ready, the project can be accessed via the url provided by Render.com.
- Deployment on other public domain is possible as well.

## Features

### 💬 Gen AI Chatbots via Groq
| Service | Model | Access Point |
|---------|-------|--------------|
| LLaMA 3.1 | 8B Instant | `/llama_reply` |
| DeepSeek | R1 Distill LLaMA 70B | `/ds_reply` |
| Moonshot AI | Kimi-K2 | Telegram bot |

- Requires to set the Groq API Key as `GROQ_API_KEY` in .env.
- `LLAMA chatbot via Groq`
  - Chat with Llama 3.1 via Groq. 
- `DeepSeek chatbot via Groq`
  - Chat with DeepSeek R1 distilled model via Groq.
- Telegram bot via webhook
  - Allows to send messages to a Telegram bot that will reply with the response of a Gen AI (Kimi-K2 from Groq).
    - Requires to set the Telegram bot token in `TELEGRAM_BOT_TOKEN` in .env.
  - `START TELEGRAM`
    - Sets webhook to the `TELEGRAM_DOMAIN_URL` in .env.
    - Now Gen AI will respond to chat messages.
  - `STOP TELEGRAM`
    - Removes the webhook set.
    - This is required before doing long polling with Telegram bot via Telegram API.
    - Sending `/stop` to the bot will also remove the webhook.

### 🛡️ Predict Spam
- Click `Predict spam` from Main.
- Web page at `/spam`
  - Enter text to predict if it is spam.
  - For a positive prediction try:
    - Money!!! You're a lucky winner! To claim your prize, call now. Over $10,000,000 in prizes!
- Logistic Regression model (`lr_model.jl`)
  - Trained from a dataset that is either spam or not spam.
  - Uses CountVectorizer `cv_model.jl` to transform text.

### 📊 Predict DBS share price
- Click `Predict DBS price` from Main.
- Web page at `/prediction`
  - Enter exchange rate to predict DBS share price.
  - Note: This was just for the sake of a classroom learning exercise!
- Numerical prediction model (`dbs.jl`)
  - Linear Regression model.
  - Trained on a dataset that relates the daily DBS share price to that day's USD to SGD exchange rate.

### 🗂️ SQLite demo
- Demonstrates SQLite for adding and deleting user records.
- `User Log`: View current user records in SQLite.
  - `Insert` to insert a new record with optional text and current timestamp.
  - `Refresh` to see current records, which could have been modified from other pages.
  - `Delete log` to delete all records.
- `Delete Log`: Delete all records in SQLite.

### 🤗 Gradio Hugging Face Integration
- `Sepia`: Embeds a Gradio app deployed on Hugging Face - [goddino-sepia2](https://huggingface.co/spaces/goddino/sepia2).
- Applies a sepia tone filter to input image.
- Outputs transformed image.
- Uses a Gradio [Interface](https://www.gradio.app/docs/gradio/interface) for image input and output.

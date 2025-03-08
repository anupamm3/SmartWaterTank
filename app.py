from flask import Flask, jsonify, render_template, request
import requests
import math
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

app = Flask(__name__)

THINGSPEAK_CHANNEL_ID = "2675402"
THINGSPEAK_READ_API_KEY = "C7UTQGLXD7CZT727"

POLL_INTERVAL = 15 

logging.basicConfig(level=logging.INFO)

last_water_level = None
second_last_water_level = None
# first mail is of user and thereafter it is neighbour mails
receiver_emails = ['123102123@nitkkr.ac.in','123102117@nitkkr.ac.in','123102119@nitkkr.ac.in']  

@app.route("/")
def index():
    return render_template("index.html", sent_email=None)

@app.route("/get_data", methods=['GET'])
def get_data_route():
    water_level, anomaly = fetch_water_level()
    if water_level is not None:
        return jsonify({"water_level": water_level, "anomaly": anomaly})
    else:
        return jsonify({"error": "Error fetching water level"}), 500

@app.route("/add_email", methods=['POST'])
def add_email():
    email = request.json.get('email')  
    if email and email not in receiver_emails:
        receiver_emails.append(email)
        logging.info(f"Added email: {email}")
        return jsonify({"message": f"Email {email} added successfully!"}), 200
    return jsonify({"error": "Invalid email or already exists."}), 400

def fetch_water_level():
    global last_water_level, second_last_water_level
    try:
        logging.info("Fetching data from ThingSpeak...")
        url = (
            f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/"
            f"feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=1"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'feeds' in data and data['feeds']:
            latest_data = data['feeds'][0]
            water_level_str = latest_data.get('field1')

            if water_level_str:
                water_level = math.floor(float(water_level_str))
                if water_level < 0:
                    water_level = 0
                logging.info(
                    f"Data fetched successfully: Current Water Level: {water_level}%"
                )

                anomaly = False
                if last_water_level is not None:
                    if abs(water_level - last_water_level) > 10:
                        anomaly = True

                second_last_water_level = last_water_level
                last_water_level = water_level

                send_email(water_level) 

                return water_level, anomaly
            else:
                logging.warning("No valid water level data available.")
                return None, False
        else:
            logging.warning("No data available from ThingSpeak.")
            return None, False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None, False


u=1;n=1

def send_email(water_level):
    global u,n
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'iot.project.nit@gmail.com'
    sender_password = 'mftb kctd mlwb qdus' 

    subject = '------Current Water Level------'
    body = f"Hi, the current water level is {water_level}%."
    neighbour_body = f"Your neighbour Harman's water tank is overflowing kindly take necessary actions."
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject

    sent_to = []

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)

        if water_level >= 100 and n==1:
            n=0
            msg['To'] = ', '.join(receiver_emails)
            msg.attach(MIMEText(neighbour_body,"plain"))
            server.sendmail(sender_email, receiver_emails, msg.as_string())
            sent_to = receiver_emails
            logging.info(
                f"Email sent successfully to {', '.join(receiver_emails)}!"
            )
        elif water_level >= 90 and u==1:
            u=0
            msg['To'] = receiver_emails[0]
            msg.attach(MIMEText(neighbour_body,"plain"))
            server.sendmail(sender_email, receiver_emails[0], msg.as_string())
            sent_to = [receiver_emails[0]]
            logging.info(f"Email sent successfully to {receiver_emails[0]}!")

    except Exception as e:
        logging.error(f"Error sending email: {e}")
    finally:
        server.quit()
    
    return sent_to

def monitor_thingspeak():
    while True:
        water_level_data = fetch_water_level()

        if water_level_data is not None:
            water_level, anomaly = water_level_data

            # logging.info(f"Water level: {water_level}%")

            if anomaly:
                logging.warning("Anomaly detected in water level!")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    thread = threading.Thread(target=monitor_thingspeak)
    thread.daemon = True
    thread.start()

    app.run(debug=True)

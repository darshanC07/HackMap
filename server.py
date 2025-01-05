# from dotenv import dotenv_values
import google.generativeai as genai
from flask import Flask,request,render_template
from flask_cors import CORS
import requests
import json, os

# secrets = dotenv_values()

app = Flask(__name__)
CORS(app)

hackathon_bucket_url = "https://hackathon-bucket.vercel.app"

mlhEvents = requests.get(url=f"{hackathon_bucket_url}/mlhEvents")
devpostEvents = requests.get(url=f"{hackathon_bucket_url}/devpostEvents")
devfolioEvents = requests.get(url=f"{hackathon_bucket_url}/devfolioEvents")

hackathons_data = {
    "mlhEvents" : {
        mlhEvents
    },
    "devpostEvents" : {
        devpostEvents
    },
    "devfolioEvents" : {
        devfolioEvents
    }
}

genai.configure(api_key=os.getenv["GEMINI_API_KEY"])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-exp-1206",
  generation_config=generation_config,
  system_instruction="You are a hackathon matcher. You will be given the user_data in json and available hackathons_data. Your task is to find the best matched hackathons for the user based on their preference. You response should be in json format. The response will be same at the data in hackathons_data but only of matched hackathons. Hackathons_data is from 3 different sites, so use whole data. Match the hackathons based on age,interested_fields,locations,known_skills,Preferred Hackathon Mode. Provide maximum of result",
)

chat_session = model.start_chat()


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/match',methods = ['POST', 'GET'])
def find_hackathons():
    if request.method == 'POST':
        print('here')
        user_data = {
            "name" : request.form.get('name'),
            "age" : request.form.get('age'),
            "location" : request.form.get('location'),
            "skills" : request.form.getlist('skills'),
            "fields" : request.form.getlist('fields'),
            "mode" : request.form.get('mode'),
            "experience" : request.form.get('experience'),
            "team-size" : request.form.get('team-size'),
            "availability" : request.form.get('availability'),
            "preferences" : request.form.get('preferences'),
        }
    
        response = chat_session.send_message(f"user_data is {user_data} and hackathon_data is {hackathons_data}")
        response_text = response.text
        final_response = response_text.replace("```","").replace("json","")
        json_data = json.loads(final_response)
        return json_data

if __name__ == "__main__":
    app.run(port=5000,debug=True)

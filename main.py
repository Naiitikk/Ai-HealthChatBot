from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random, os

app = FastAPI(title="YourHealth AI - Offline Chatbot")

# Templates and static
templates = Jinja2Templates(directory="templates")
os.makedirs("static/profile_pics", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory temporary profile (session-like)
profile_data = {}

# Content pools
daily_thoughts = [
    "Health is the real wealth — invest in it every day.",
    "Small steps every day lead to lifelong wellbeing.",
    "Breathe. Move. Nourish."
]

meal_suggestions = [
    "Quinoa & chickpea salad — fiber and plant protein.",
    "Grilled salmon bowl — omega-3s and greens.",
    "Vegetable dal with brown rice — balanced and comforting."
]

wellness_suggestions = [
    "Sun Salutation (Surya Namaskar) — 5–10 rounds to energize.",
    "Box breathing — inhale 4s, hold 4s, exhale 4s, hold 4s, repeat.",
    "Guided body scan — 10 minutes to release tension."
]

# Simple health knowledge (offline fallback)
health_knowledge = {
    "cold": "Common cold: runny/stuffy nose, sore throat, mild cough. Rest and fluids.",
    "flu": "Flu: fever, body aches, fatigue. Seek care if high risk or severe symptoms.",
    "covid": "COVID-19: fever, cough, loss of taste/smell. Isolate if symptomatic and seek testing.",
    "diabetes": "Diabetes: increased thirst, frequent urination. Manage with diet and medical care.",
}

@app.get('/', response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse('chat.html', {
        'request': request,
        'profile': profile_data if profile_data else None,
        'reply': None,
        'daily_thought': random.choice(daily_thoughts),
        'meal_suggestion': random.choice(meal_suggestions),
        'wellness_suggestion': random.choice(wellness_suggestions),
    })

@app.post('/', response_class=HTMLResponse)
async def post_index(request: Request,
                     message: str = Form(...),
                     username: str = Form(None),
                     name: str = Form(None),
                     profile_pic: UploadFile = File(None)):
    # Save temporary profile if provided
    if username and name:
        profile_data['username'] = username
        profile_data['name'] = name
        if profile_pic:
            filename = f"{username}_{profile_pic.filename}"
            out_path = os.path.join('static', 'profile_pics', filename)
            with open(out_path, 'wb') as f:
                f.write(profile_pic.file.read())
            profile_data['profile_pic'] = f"/{out_path}"

    # Generate reply: try keyword match then fallback
    msg = message.lower()
    reply = None
    for key, info in health_knowledge.items():
        if key in msg:
            reply = info
            break

    if not reply:
        # Simple AI-like variation using templates
        templates_variations = [
            "Thanks for asking — here's a general health tip: {tip}",
            "Here's a helpful note: {tip}",
            "Quick wellness suggestion: {tip}"
        ]
        tip = random.choice(list(health_knowledge.values())) if random.random() < 0.4 else random.choice(meal_suggestions + wellness_suggestions)
        reply = random.choice(templates_variations).format(tip=tip)

    return templates.TemplateResponse('chat.html', {
        'request': request,
        'profile': profile_data if profile_data else None,
        'reply': reply,
        'daily_thought': random.choice(daily_thoughts),
        'meal_suggestion': random.choice(meal_suggestions),
        'wellness_suggestion': random.choice(wellness_suggestions),
    })

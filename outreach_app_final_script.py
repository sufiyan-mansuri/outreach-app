import streamlit as st
import pandas as pd
import yagmail
import time
import random
from openai import OpenAI

# --- UI Layout ---
st.title("📺 YouTube Creator Outreach")

uploaded_file = st.file_uploader("Upload your YouTube leads CSV", type=["csv"])

st.subheader("✉️ Gmail Credentials")
gmail_user = st.text_input("Your Gmail Address")
gmail_app_password = st.text_input("Gmail App Password", type="password")

st.subheader("🧠 OpenAI Settings")
openai_api_key = st.text_input("OpenAI API Key (GPT-3.5)", type="password")

# --- Email Generation Function ---
def generate_email(channel_name, about_us, subscribers, api_key):
    openai.api_key = api_key

    prompt = f"""
You're a professional video editor named Aimaan reaching out to YouTube creators.

Generate a short, casual outreach email body based on this info. Structure it into exactly 3 paragraphs:

1. Compliment the creator's content based on their description.
2. Introduce yourself as Aimaan, a video editor with 2B+ views.
3. Offer to do one free edit, mention your site (aimaanedits.com), and invite collaboration.

❌ Do NOT include any closing line like "Thanks", "Regards", "Looking forward...", or "Would be dope to connect."
❌ Do NOT sign off with your name — leave that for the fixed footer.

Just return the 3 paragraphs only. No extra lines or signature.

Details:
Channel Name: {channel_name}
About Us: {about_us}
Subscribers: {subscribers}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    body = response['choices'][0]['message']['content'].strip()

    # Normalize paragraph spacing
    paragraphs = [p.strip() for p in body.split("\n") if p.strip()]
    body_clean = "\n\n".join(paragraphs)

    # Signature (no space above, no space between)
    signature = (
        "Best,<br>"
        "Aimaan<br>"
        '<a href="https://www.instagram.com/aimaanedits" target="_blank">Instagram</a>'
    )

    final_body = body_clean.replace("\n", "<br>") + "<br><br>" + signature
    return final_body

# --- Email Sending ---
if st.button("🚀 Start Sending Emails"):
    if not uploaded_file or not gmail_user or not gmail_app_password or not openai_api_key:
        st.error("⚠️ Please complete all fields and upload your CSV.")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
        yag = yagmail.SMTP(gmail_user, gmail_app_password)
        sent_count = 0
        status_placeholder = st.empty()

        for idx, row in df.iterrows():
            email = row.get("email") or row.get("Email")
            channel_name = row.get("Channel Name") or "there"
            about_us = row.get("About Us") or "a great creator"
            subscribers = row.get("Subscribers") or "unknown"

            if not email or "@" not in str(email):
                status_placeholder.warning(f"⚠️ Skipping row {idx} — invalid email.")
                continue

            try:
                email_content = generate_email(channel_name, about_us, subscribers, openai_api_key)
                subject = f"Let's work on something for {channel_name}"
                yag.send(to=email, subject=subject, contents=[email_content])
                status_placeholder.success(f"✅ Sent to {email}")
                sent_count += 1
                time.sleep(random.randint(40, 90))

            except Exception as e:
                status_placeholder.error(f"❌ Failed to send to {email}: {e}")

        st.info(f"🎉 Finished — {sent_count} emails sent!")

    except Exception as e:
        st.error(f"❌ Failed to process file or send emails: {e}")

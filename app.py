try:
    import audioop
except ImportError:
    import sys
    try:
        import audioop_lts as audioop
        sys.modules['audioop'] = audioop
    except ImportError:
        pass

import streamlit as st
import os
import sys
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import importlib.util

# Dynamic import for the mashup script since it starts with a number
spec = importlib.util.spec_from_file_location("mashup_script", "102316122.py")
mashup_script = importlib.util.module_from_spec(spec)
sys.modules["mashup_script"] = mashup_script
spec.loader.exec_module(mashup_script)

# Function to zip the file
def zip_file(output_file, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(output_file, os.path.basename(output_file))

# Function to send email
def send_email(receiver_email, attachment_path):
    sender_email = "kkandhari_be23@thapar.edu"
    sender_password = "besp tzpv oftu svcd"
    


    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Your Mashup is Ready!"
    
    body = "Here is the mashup you requested. Enjoy!"
    msg.attach(MIMEText(body, 'plain'))
    
    filename = os.path.basename(attachment_path)
    attachment = open(attachment_path, "rb")
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# Custom CSS for "Beautiful" Design (Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: 'Outfit', sans-serif;
    }

    /* Glassmorphism Container */
    .stForm {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }

    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 10px !important;
    }

    h1 {
        font-weight: 700;
        letter-spacing: -1px;
        background: -webkit-linear-gradient(white, #ccc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .stButton > button {
        background: linear-gradient(45deg, #ff4b2b, #ff416c);
        border: none;
        border-radius: 12px;
        color: white;
        padding: 15px 32px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s ease;
        width: 100%;
        margin-top: 20px;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
    }

    /* Success/Error Styling */
    .stAlert {
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎵 MP3 Mashup Generator")
st.markdown("### Create your custom mashup and get it via email!")

with st.form("mashup_form"):
    col1, col2 = st.columns(2)
    with col1:
        singer = st.text_input("Singer Name", placeholder="e.g., Arijit Singh")
        num_videos = st.number_input("Number of Videos", min_value=11, value=11, help="Must be greater than 10")
    
    with col2:
        duration = st.number_input("Duration (sec)", min_value=21, value=25, help="Must be greater than 20")
        email_id = st.text_input("Email Id", placeholder="name@example.com")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not singer or not email_id:
        st.warning("Please fill in all fields.")
    elif num_videos <= 10:
        st.error("Number of videos must be greater than 10.")
    elif duration <= 20:
        st.error("Duration must be greater than 20 seconds.")
    else:
        output_filename = "mashup.mp3"
        zip_filename = "mashup.zip"
        
        with st.spinner(f"Creating mashup for {singer}... This process ensures unique songs and high quality!"):
            try:
                # 0. Cleanup previous downloads
                if os.path.exists("downloads"):
                    for f in os.listdir("downloads"):
                        os.remove(os.path.join("downloads", f))

                # 1. Download
                status_text = st.empty()
                status_text.text("Downloading videos... (This takes time)")
                mashup_script.download_videos(singer, num_videos)
                
                # 2. Convert & Trim
                status_text.text("Processing audio...")
                audio_files = mashup_script.convert_and_trim(duration)
                
                # 3. Merge
                status_text.text("Merging tracks...")
                mashup_script.merge_audios(audio_files, output_filename)
                
                # 4. Zip
                status_text.text("Zipping file...")
                zip_file(output_filename, zip_filename)
                
                # 5. Email
                status_text.text(f"Sending email to {email_id}...")
                if send_email(email_id, zip_filename):
                    st.success(f"✅ Mashup sent successfully to {email_id}!")
                    st.balloons()
                else:
                    st.error("❌ Failed to send email. Check credentials in source code.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Cleanup
                if os.path.exists(output_filename):
                    os.remove(output_filename)
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
                # Note: 'downloads' folder cleanup is left as exercise or manual

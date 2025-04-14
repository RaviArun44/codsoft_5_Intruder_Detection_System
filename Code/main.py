import cv2
import streamlit as st
from datetime import datetime
import os
import pandas as pd
from email.message import EmailMessage
import smtplib
import pygame

# === CONFIGURATION ===
SAVE_DIR = "intruders"
LOG_FILE = "detection_log.csv"
ALERT_SOUND = r"C:\Users\MUIS\OneDrive - Eltronic Group A S\Desktop\ArunProject\Intruder_Alert_System\alert_sound.mp3"
EMAIL_SENDER = "2312402@nec.edu.in"
EMAIL_PASSWORD = "zlww daok mbev ufyy"
EMAIL_RECEIVER = "muthuishwarya0705@gmail.com"
EMAIL_ALERT = True

os.makedirs(SAVE_DIR, exist_ok=True)
pygame.mixer.init()

# === Load Face Detection Model ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# === Streamlit App Settings ===
st.set_page_config(page_title="Intruder Detection System", layout="wide")
st.markdown("<h1 style='color:#ff4c4c;'>Intruder Detection System</h1>", unsafe_allow_html=True)
st.sidebar.header("🛠️ Control Panel")

# === State Initialization ===
if "cap" not in st.session_state:
    st.session_state.cap = None
if "running" not in st.session_state:
    st.session_state.running = False

# === Sidebar Controls ===
camera_toggle = st.sidebar.toggle("Camera")

color_format = st.sidebar.selectbox("Color Format", ["BGR", "RGB", "Grayscale"])

if camera_toggle and not st.session_state.running:
    st.session_state.cap = cv2.VideoCapture(0)
    st.session_state.running = True
    st.sidebar.success("✅ Camera started.")

elif not camera_toggle and st.session_state.running:
    if st.session_state.cap is not None:
        st.session_state.cap.release()
    st.session_state.cap = None
    st.session_state.running = False
    st.sidebar.info("⛔ Camera stopped.")

save_btn = st.sidebar.button("Save Current Frame")
show_logs = st.sidebar.checkbox("Show Detection Logs")

# === Email Function ===
def send_email_alert(image_path):
    msg = EmailMessage()
    msg["Subject"] = "📸 Intruder Alert"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content("An intruder has been detected. See the attached image.")

    with open(image_path, "rb") as img:
        msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename=os.path.basename(image_path))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Email failed: {e}")
        return False

# === Logging Function ===
def log_detection(filename, face_count, email_status):
    log_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "File": filename,
        "Faces Detected": face_count,
        "Email Sent": email_status
    }

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([log_entry])

    df.to_csv(LOG_FILE, index=False)

# === Frame Display Placeholder ===
frame_placeholder = st.empty()

# === Main Camera Loop ===
if st.session_state.running and st.session_state.cap is not None:
    ret, frame = st.session_state.cap.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        face_count = len(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        st.subheader(f"🧍 Faces Detected: {face_count}")

        if face_count > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intruder_{timestamp}.jpg"
            image_path = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(image_path, frame)

            pygame.mixer.music.load(ALERT_SOUND)
            pygame.mixer.music.play()

            email_sent = False
            if EMAIL_ALERT:
                email_sent = send_email_alert(image_path)
                if email_sent:
                    st.success("Email sent successfully.")

            st.success(f"📸 Intruder image saved: `{filename}`")
            log_detection(filename, face_count, email_sent)

        # Apply selected color format
        if color_format == "RGB":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            channels = "RGB"
        elif color_format == "Grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            channels = "RGB"
        else:
            channels = "BGR"

        frame_placeholder.image(frame, channels=channels, use_container_width=True)

        if save_btn:
            manual_filename = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            save_path = os.path.join(SAVE_DIR, manual_filename)
            cv2.imwrite(save_path, frame)
            st.sidebar.success(f"Frame saved manually: `{manual_filename}`")
            log_detection(manual_filename, 0, False)
    else:
        st.warning("⚠️ Could not read frame. Try restarting the camera.")

# === Display Logs with Filter & Export ===
if show_logs:
    st.subheader("Detection Log History")

    if os.path.exists(LOG_FILE):
        df_logs = pd.read_csv(LOG_FILE)

        # Filter by Email Sent status
        filter_option = st.selectbox("Filter by Email Status", ["All", "Sent", "Not Sent"])
        if filter_option == "Sent":
            df_logs = df_logs[df_logs["Email Sent"] == True]
        elif filter_option == "Not Sent":
            df_logs = df_logs[df_logs["Email Sent"] == False]

        st.dataframe(df_logs, use_container_width=True)

        # Download as CSV
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇Download Log as CSV",
            data=csv,
            file_name="filtered_detection_log.csv",
            mime="text/csv",
        )

        # Show saved intruder images
        show_images = st.checkbox("Show Recent Intruder Images")
        if show_images:
            for _, row in df_logs.tail(5).iterrows():
                img_path = os.path.join(SAVE_DIR, row["File"])
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"{row['Timestamp']} | Faces: {row['Faces Detected']}", use_container_width=True)
    else:
        st.info("No detection logs found yet.")

# Real-Time Intruder Detection & Alert System 📸

This project involves the development of a **Real-Time Intruder Detection & Alert System** that uses computer vision and facial recognition to detect intruders via a live camera feed. Upon detecting an intruder, the system sends an email alert with an image attachment and plays an audio alarm.

## Project Overview

The **Real-Time Intruder Detection & Alert System** continuously monitors the live camera feed, detecting faces using **OpenCV**. If an intruder is detected, the system triggers:
- **Email Alert**: Sends an email with an attached image of the intruder.
- **Audio Alert**: Plays a pre-recorded sound to notify users of the intrusion.
- **Detection Logs**: Maintains logs of all intrusions with timestamps and exportable logs for records.

## Features

- **Face Detection**: Uses OpenCV's Haar Cascade Classifier to detect faces in real-time from the camera feed.
- **Real-time Alerts**:
  - **Email Notifications** with intruder image attachment.
  - **Audio Alerts** to notify of intrusion.
- **Detection Logs**: Saves the intrusion event details in a CSV log file, including timestamps, the number of faces detected, and email status.
- **Manual Frame Saving**: Option to save frames manually from the live feed for later review.
- **Streamlit Web Interface**: Simple UI for toggling the camera, viewing the live feed, and controlling alerts.

## Technologies Used

- **Python**: The programming language used for implementing the system.
- **OpenCV**: Library for real-time computer vision and face detection.
- **Streamlit**: Web app framework for displaying the live feed and control options.
- **smtplib**: For sending email alerts with image attachments.
- **playsound**: For playing audio alerts.
- **Pandas**: For managing and exporting detection logs to CSV.

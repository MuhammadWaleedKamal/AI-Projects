# 🚗 Interactive Car Annotation Game using YOLO & OpenCV

This project is an **interactive computer vision game** built using **OpenCV and YOLO (Ultralytics)**.  
The YOLO model first detects **cars in an image**, and then the **user manually annotates the correctly predicted cars** by drawing bounding boxes — turning object detection into a fun and engaging game.

---

## 🔍 How It Works

1. A YOLO model predicts all cars present in the input image.
2. The predicted bounding boxes are stored internally (hidden from the user).
3. The user draws rectangles over cars using the mouse.
4. The system validates whether the drawn box correctly matches a predicted car.
5. Feedback is shown in real-time:
   - ✅ Correct selection  
   - ❌ Wrong or wide selection  
   - ⚠️ Already selected car  
6. The game ends once **all predicted cars are correctly annotated**.

---

## 🎮 Features

- YOLO-based car detection  
- Mouse-based manual annotation using OpenCV  
- Real-time validation of bounding boxes  
- Interactive messages and scoring system  
- Countdown-based game start  
- Win message after successful annotation of all cars  

---

## 🛠️ Technologies Used

- Python  
- OpenCV  
- Ultralytics YOLO  
- NumPy  

---

## 📌 Use Cases

- Learning object detection concepts  
- Understanding bounding box evaluation  
- Annotation practice for computer vision datasets  
- Gamified computer vision learning experience  

---

## ▶️ How to Run

```bash
pip install ultralytics opencv-python numpy
python main.py
```

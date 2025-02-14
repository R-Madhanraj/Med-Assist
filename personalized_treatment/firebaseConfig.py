
import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyB_b-d4xCczTcNqdoKj8l8bHT2uqb-qT08",
  "authDomain": "hackathon-a3afe.firebaseapp.com",
  "databaseURL": "https://hackathon-a3afe-default-rtdb.firebaseio.com",
  "projectId": "hackathon-a3afe",
  "storageBucket": "hackathon-a3afe.firebasestorage.app",
  "messagingSenderId": "603609129154",
  "appId": "1:603609129154:web:0e3d836950f764877c1b5b",
  "measurementId": "G-T0EWLHSL13"
};

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()  # Optional, only if you use Realtime DB (can be skipped if using Firestore)

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAQ5Sty_qAzOBtd_h2gFTGEC5sHH3_fNWE",
  authDomain: "theinternetparty-5b902.firebaseapp.com",
  databaseURL: "https://theinternetparty-5b902-default-rtdb.firebaseio.com",
  projectId: "theinternetparty-5b902",
  storageBucket: "theinternetparty-5b902.appspot.com",
  messagingSenderId: "372100457867",
  appId: "1:372100457867:web:e842fec6b1bf2ad40dbb8e",
  measurementId: "G-55X9M772TC"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get a reference to the Firebase Auth service
const auth = firebase.auth();
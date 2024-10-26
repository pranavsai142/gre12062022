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

// Function to handle login
function handleRegister() {
    //Clear errorMessage span
    document.getElementById("errorMessage").textContent=""
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    if(password != confirmPassword) {
        document.getElementById("errorMessage").textContent="Passwords do not match."
    } else {
        auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Signed in 
            var user = userCredential.user;
            console.log("User registered:", user);
            // Here you might want to notify the server or update UI
        })
        .catch((error) => {
            var errorCode = error.code;
            var errorMessage = error.message;
            console.error("Register error:", errorCode, errorMessage);
            document.getElementById("errorMessage").textContent=errorMessage
            // Display error to user
        });
    }
    firebase.auth().onAuthStateChanged(user => {
        if (user) {
            user.getIdToken().then(idToken => {
                fetch('/validate-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ idToken })
                }).then(response => {
                    if (response.redirected) {
                        window.location.href = response.url; // Redirect to the new URL
                    } else if (!response.ok) {
                        return response.json().then(data => {
                            if (data.authenticated === false) {
                                console.error("Authentication failed:", data);
                            }
                        });
                    }
                }).catch(error => {
                    console.error("Error validating token:", error);
                });
            });
        } else {
            console.log("No user is signed in.");
        }
    });
}

// Add event listener to the login button
document.getElementById('registerButton').addEventListener('click', handleRegister);
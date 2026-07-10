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

const auth = firebase.auth();

function showRegisterError(message) {
  const errEl = document.getElementById("errorMessage");
  if (!errEl) return;
  if (!message) {
    errEl.textContent = "";
    errEl.style.display = "none";
    return;
  }
  errEl.textContent = message;
  errEl.style.display = "block";
}

/** Exchange Firebase ID token for a Flask session, then follow redirect to /account. */
function establishServerSession(idToken) {
  return fetch("/validate-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idToken: idToken }),
  }).then(function (response) {
    if (response.redirected) {
      window.location.href = response.url;
      return;
    }
    if (!response.ok) {
      return response
        .json()
        .then(function (data) {
          showRegisterError(
            (data && (data.error || data.message)) ||
              "Authentication failed. Please try again."
          );
        })
        .catch(function () {
          showRegisterError("Authentication failed. Please try again.");
        });
    }
  });
}

function handleRegister() {
  showRegisterError("");
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (password !== confirmPassword) {
    showRegisterError("Passwords do not match.");
    return;
  }

  // One-shot path: create user → token → server session.
  // Do NOT register onAuthStateChanged here — each click would stack listeners.
  auth
    .createUserWithEmailAndPassword(email, password)
    .then(function (userCredential) {
      return userCredential.user.getIdToken();
    })
    .then(establishServerSession)
    .catch(function (error) {
      console.error("Register error:", error.code, error.message);
      showRegisterError(error.message || "Registration failed.");
    });
}

document.getElementById("registerButton").addEventListener("click", handleRegister);

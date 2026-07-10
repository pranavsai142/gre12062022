// Firebase password reset — same project config as login/register.
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

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

function showResetMessage(message, isError) {
  const errEl = document.getElementById("errorMessage");
  const okEl = document.getElementById("successMessage");
  if (errEl) {
    errEl.style.display = "none";
    errEl.textContent = "";
  }
  if (okEl) {
    okEl.style.display = "none";
    okEl.textContent = "";
  }
  if (!message) return;
  if (isError && errEl) {
    errEl.textContent = message;
    errEl.style.display = "block";
  } else if (!isError && okEl) {
    okEl.textContent = message;
    okEl.style.display = "block";
  }
}

function handleReset() {
  showResetMessage("");
  const emailInput = document.getElementById("email");
  const email = (emailInput && emailInput.value || "").trim();
  if (!email) {
    showResetMessage("Enter the email address for your membership.", true);
    return;
  }

  const btn = document.getElementById("resetButton");
  if (btn) btn.disabled = true;

  // Firebase sends the reset email; continueUrl returns members to our login.
  const actionCodeSettings = {
    url: window.location.origin + "/login",
    handleCodeInApp: false,
  };

  auth
    .sendPasswordResetEmail(email, actionCodeSettings)
    .then(function () {
      showResetMessage(
        "If an account exists for that email, a reset link is on the way. Check your inbox (and spam), then sign in.",
        false
      );
    })
    .catch(function (error) {
      console.error("Reset error:", error.code, error.message);
      // Avoid account enumeration: same friendly message for user-not-found
      if (error.code === "auth/user-not-found") {
        showResetMessage(
          "If an account exists for that email, a reset link is on the way. Check your inbox (and spam), then sign in.",
          false
        );
      } else if (error.code === "auth/invalid-email") {
        showResetMessage("That email address does not look valid.", true);
      } else if (error.code === "auth/too-many-requests") {
        showResetMessage("Too many attempts. Wait a minute and try again.", true);
      } else {
        showResetMessage(error.message || "Could not send reset email.", true);
      }
    })
    .finally(function () {
      if (btn) btn.disabled = false;
    });
}

var resetBtn = document.getElementById("resetButton");
if (resetBtn) {
  resetBtn.addEventListener("click", handleReset);
}
var emailEl = document.getElementById("email");
if (emailEl) {
  emailEl.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") {
      ev.preventDefault();
      handleReset();
    }
  });
}

// Voting dashboard JS — follows the exact same fetch + alert + "fish" error style
// used by draft.js, detail.js, and all other interactive pages.

function collectVotes() {
    const votes = {};
    // Find every checked radio whose name starts with "vote-"
    const checked = document.querySelectorAll('input[type="radio"]:checked');
    checked.forEach(radio => {
        if (radio.name && radio.name.startsWith('vote-')) {
            const key = radio.name.replace('vote-', '');
            votes[key] = radio.value;
        }
    });
    return votes;
}

/** Prefer explicit data-window-id (server-rendered). Never scrape prose. */
function getBallotWindowId() {
    const root = document.querySelector('[data-window-id]');
    if (root) {
        const w = (root.getAttribute('data-window-id') || '').trim();
        if (w) return w;
    }
    const clock = document.querySelector('[data-voting-clock][data-window-id]');
    if (clock) {
        const w = (clock.getAttribute('data-window-id') || '').trim();
        if (w) return w;
    }
    return null;
}

const submitBtn = document.getElementById('submitBallot');
if (submitBtn) {
    submitBtn.addEventListener('click', function(event) {
        event.preventDefault();

        const votes = collectVotes();
        const windowId = getBallotWindowId();

        // With abstain as the default, an untouched ballot will submit all abstains.
        // Only block if there are literally no items to vote on.
        if (Object.keys(votes).length === 0) {
            alert("There are no items on this ballot to vote on.");
            return;
        }

        if (!confirm("You can only cast ONE ballot per voting window. Your choices will be final for " + (windowId || "this week") + ". Submit now?")) {
            return;
        }

        fetch('/submit-ballot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                windowId: windowId,
                votes: votes
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || "Ballot recorded. Thank you for participating in The Internet Party.");
                window.location.reload();
            } else {
                alert(data.error || "Something went wrong while recording your ballot.");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Network error while submitting ballot. Please try again.");
        });
    });
}

// Close / Promote button (manual tabulation + promotion per approved plan)
const closeBtn = document.getElementById('closeWindowBtn');
if (closeBtn) {
    closeBtn.addEventListener('click', function(event) {
        event.preventDefault();

        if (!confirm("This will tally all votes for the current window and promote any items that received more Yes than No votes.\n\nContinue?")) {
            return;
        }

        const windowId = getBallotWindowId();

        fetch('/close-window', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ windowId: windowId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const msg = (data.result && data.result.message) || "Window closed and winners promoted.";
                alert(msg);
                window.location.reload();
            } else {
                alert(data.error || "Could not close window.");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Network error while closing window.");
        });
    });
}
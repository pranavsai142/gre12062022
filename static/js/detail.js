document.getElementById('saveDraft').addEventListener('click', function(event) {
    const id = document.getElementById('policyId').innerText;
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    console.log('Saving draft...' + id);

    fetch('/update-draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            id: id,
            title: title,
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Draft saved successfully.');
            // Optionally, you might want to clear the form or navigate to another page
            // window.location.href = "/policy"; // Redirect to policy page if needed
        } else {
            alert(data.error);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving the draft.');
    });
});

document.getElementById('submitDraft').addEventListener('click', function(event) {
    const id = document.getElementById('policyId').innerText;
    if(confirm("Warning! Any unsaved changes will not be submitted.")) {
        console.log('Submitting draft...', id);
        fetch('/submit-draft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Draft submitted successfully! Congratulations!');
                document.getElementById('draftForm').reset();
                // Optionally, you might want to clear the form or navigate to another page
                // window.location.href = "/policy"; // Redirect to policy page if needed
            } else {
                alert(data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while submitting the draft.');
        });
    }
});

document.getElementById('removeDraft').addEventListener('click', function(event) {
    const id = document.getElementById('policyId').innerText;
    if(confirm("The draft is irrecoverable, please confirm removal.")) {
        console.log('Submitting draft...', id);
        fetch('/remove-draft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: id,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Draft removed successfully.');
                document.getElementById('draftForm').reset();
                // Optionally, you might want to clear the form or navigate to another page
                // window.location.href = "/policy"; // Redirect to policy page if needed
            } else {
                alert(data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while removing the draft.');
        });
    }
});
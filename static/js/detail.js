document.getElementById('draftForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    const action = formData.get('action');
    console.log(action);
    
    const id = document.getElementById('policyId').innerText;
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    console.log(id)

    if(action === 'save') {
        // Handle save draft logic
        console.log('Saving draft...');

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
                alert('Draft created successfully');
                // Optionally, you might want to clear the form or navigate to another page
                document.getElementById('draftForm').reset();
                // window.location.href = "/policy"; // Redirect to policy page if needed
            } else {
                alert(data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while creating the draft.');
        });
        // AJAX call to save draft
    } else if(action === 'submit' && alert("Warning! Any unsaved edits will not be submitted!")) {
    
        // Handle submit draft logic
        console.log('Submitting draft...');
        fetch('/submit-draft', {
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
                alert('Draft created successfully');
                // Optionally, you might want to clear the form or navigate to another page
                document.getElementById('draftForm').reset();
                // window.location.href = "/policy"; // Redirect to policy page if needed
            } else {
                alert(data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while creating the draft.');
        });
        // AJAX call to submit draft
    }
});

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
        alert('An error occurred while creating the draft.');
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
                // Optionally, you might want to clear the form or navigate to another page
                // window.location.href = "/policy"; // Redirect to policy page if needed
            } else {
                alert(data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while creating the draft.');
        });
    }
});
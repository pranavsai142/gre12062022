document.getElementById('draftForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    
    fetch('/create-draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
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
});
document.getElementById('login-form').onsubmit = function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${username}&password=${password}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            // Save the token in sessionStorage (or localStorage)
            sessionStorage.setItem('jwt_token', data.token);
            window.location.href = '/todo'; // Redirect to the tasks page
        } else {
            alert('Login failed!');
        }
    })
    .catch(error => console.error('Error:', error));
};

// Function to make a request with the JWT token
function makeAuthenticatedRequest(url) {
    const token = sessionStorage.getItem('jwt_token');
    if (!token) {
        alert('Please log in first');
        return;
    }

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => console.error('Error:', error));
}

// Handle logout
document.getElementById('logout-btn').onclick = function() {
    sessionStorage.removeItem('jwt_token');
    window.location.href = '/'; // Redirect to login page
};

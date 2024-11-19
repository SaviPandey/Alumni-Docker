const form = document.querySelector('.search-form');

// Listen for form submission
form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent the form from submitting normally

    // Get the value of the input field
    const inputValue = form.querySelector('input[name="query"]').value;

    // Construct the URL with the input value
    const url = `/search/${encodeURIComponent(inputValue)}`;

    // Redirect to the URL
    window.location.href = url;
});
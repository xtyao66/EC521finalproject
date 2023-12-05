function getParameterByName(name, url = window.location.href) {
    return decodeURIComponent(new URL(url).searchParams.get(name));
}

function goToOriginalUrl() {
    const originalUrl = getParameterByName('goto');
    const token = getParameterByName('token');

    let url = new URL(originalUrl);
    url.searchParams.append('msafebrowsing_access_token', token); // Adds the token parameter

    window.location.href = url.href; // Navigates to the modified URL
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('proceedButton').addEventListener('click', goToOriginalUrl);
    const url = getParameterByName('goto'); // Get the URL parameter
    // Set the URL in the div
    document.getElementById('urlDisplay').textContent = url;
});

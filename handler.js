window.onload = function () {
    const url = new URL(window.location.href);
    const originalUrl = decodeURIComponent(url.searchParams.get('url'));
    const token = decodeURIComponent(url.searchParams.get('token'));

    let urlTo = new URL(originalUrl);
    urlTo.searchParams.append('msafebrowsing_access_token', token); // Adds the token parameter

    document.getElementById('continueLink').href = urlTo.href;

    const headerToken = "cNh$gVrbEK%2WSU7*iX@HEoN79wF";

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://108.26.205.240:9090/predict1?url=" + encodeURIComponent(new URL(originalUrl).href), true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            // Check if the request was successful
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                if (response["prediction"] == "Malicious") {
                    window.location.href = 'warning.html?goto=' + encodeURIComponent(originalUrl)
                        + "&token=" + encodeURIComponent(token);
                } else if (response["prediction"] == "Benign") {
                    const pormpt = document.getElementById("checkingSafety");
                    pormpt.innerText = "You're in safe zone, redirecting...";
                    pormpt.style = "color: green";
                    let url = new URL(originalUrl);
                    if ('signature' in response) {
                        url.searchParams.append('msafebrowsing_access_token', 'ECDSA'); // Adds the token parameter
                        url.searchParams.append('msafebrowsing_ecdsa_token', response['signature'])
                    } else {
                        url.searchParams.append('msafebrowsing_access_token', token); // Adds the token parameter
                    }

                    window.location.href = url.href; // Navigates to the modified URL
                }
            } else {
                const pormpt = document.getElementById("checkingSafety");
                pormpt.innerText = "There was a network issue";
                pormpt.style = "color: red";
            }
        }
    };
    xhr.send();
}

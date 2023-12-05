let nonceMap = {};
let allowOrigin = {};

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        // confirm("in " +  JSON.stringify(details));
      // Check if the request is of type 'main_frame', which indicates a new page load or navigation
        if (details.type === 'main_frame' && details.method === 'GET') {
            // confirm(JSON.stringify(nonceMap));
            // confirm(details.url);
            const urlObj = new URL(details.url);
            const origin = urlObj.origin; // Extracts the origin part of the URL
            // confirm('Checking origin ' + origin);
            // confirm("orogins " + JSON.stringify(allowOrigin));
            if (origin in allowOrigin) {
                return { cancel: false };
            }
            if (nonceMap[origin]) {
                // confirm('got token ' + urlObj.searchParams.get('msafebrowsing_access_token') + " ct" + nonceMap[origin]);
                if (urlObj.searchParams.get('msafebrowsing_access_token') === nonceMap[origin]) {
                    // confirm('1');
                    allowOrigin[origin] = Date.now();
                    urlObj.searchParams.delete('msafebrowsing_access_token');
                    return { 
                        redirectUrl: urlObj.href
                    };
                }
            }
            const nonce = generateNonce(); // Function to generate a unique nonce
            nonceMap[origin] = nonce;
            // Redirect to a local handler that will do the check and then redirect accordingly
            return { 
                redirectUrl: 
                chrome.extension.getURL('localHandler.html?url=' 
                    + encodeURIComponent(details.url)
                    + "&token="
                    + encodeURIComponent(nonce)) 
            };
        }
      return { cancel: false };
    },
    { urls: ["*://*/*"] },
    ["blocking"]
  );
  
function isUrlMalicious(url) {
    // Implement your logic or API call here
    // This is a placeholder function
    // For real use, you would make an asynchronous API call
    // Note: Synchronous XMLHttpRequests in the background script are generally discouraged
    return true;  // Replace with actual logic
  }
  
  function generateNonce() {
    const now = Date.now(); // Current time
    const random = Math.random().toString(36).substring(2, 15); // Random string
    return `${now}-${random}`;
}

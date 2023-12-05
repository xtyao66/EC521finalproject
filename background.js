let nonceMap = {};
let allowOrigin = {};

let keyPair = [];
let pluginOpt = [];

function matchRuleShort(str, rule) {
  var escapeRegex = (str) => str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
  return new RegExp("^" + rule.split("*").map(escapeRegex).join(".*") + "$").test(str);
}

function isMatch(url, regexPatterns) {
  // Split the patterns into an array
  const patterns = regexPatterns.split(';').map(pattern => pattern.trim());

  // Iterate over each pattern
  for (let i = 0; i < patterns.length; i++) {
      // Test if the url matches the current pattern
      if (matchRuleShort(url, patterns[i])) {
          return true; // Return true if there is a match
      }
  }

  return false; // Return false if no patterns matched
}


chrome.webRequest.onBeforeRequest.addListener(
  function (details) {
    // confirm("in " +  JSON.stringify(details));
    // Check if the request is of type 'main_frame', which indicates a new page load or navigation
    if (details.type === 'main_frame' && details.method === 'GET') {
      // confirm(JSON.stringify(nonceMap));
      // confirm(details.url);
      const urlObj = new URL(details.url);
      const origin = urlObj.origin; // Extracts the origin part of the URL

      console.log(urlObj);
      // load plugin options
      if (pluginOpt.mode) {
        if (pluginOpt.mode === "disabled") {
          // Continue navigation
          return {}
        } else if (isMatch(urlObj.href, pluginOpt.list)) {
          if (pluginOpt.mode === "blacklist") {
            // Continue the control flow, do nothing
          } else {
            return {}
          }
        }
      }
      // confirm('Checking origin ' + origin);
      // confirm("orogins " + JSON.stringify(allowOrigin));
      if (origin in allowOrigin) {
        return { cancel: false };
      }
      if (nonceMap[origin]) {
        // confirm('got token ' + urlObj.searchParams.get('msafebrowsing_access_token') + " ct" + nonceMap[origin]);
        if (urlObj.searchParams.get('msafebrowsing_access_token') === nonceMap[origin]) {
          nonceMap[origin] = undefined; // revoke the nonce
          urlObj.searchParams.delete('msafebrowsing_access_token');
          // confirm user override
          if (confirm('Insist on visiting this url? ' + urlObj.href)) {
            allowOrigin[origin] = Date.now();
            return {
              redirectUrl: urlObj.href
            };
          } else {
            return {
              redirectUrl: "https://google.com/"
            };
          }
        } else if (urlObj.searchParams.get('msafebrowsing_access_token') === "ECDSA") {

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

async function generateKeyPair() {
  return await window.crypto.subtle.generateKey({
    name: "ECDSA",
    namedCurve: "P-256" // Can be "P-256", "P-384", or "P-521"
  }, true, ["sign", "verify"]);
}

function generateNonce() {
  const now = Date.now(); // Current time
  const random = Math.random().toString(36).substring(2, 15); // Random string
  return `${now}-${random}`;
}

generateKeyPair().then((kp) => {
  keyPair = kp;
});

async function loadStorageValue() {
  chrome.storage.sync.get(
    { pluginMode: 'enabled', pluginWhitelist: "*://*.google.com/*;\nhttps://*.youtube.com/*" },
    (items) => {
      pluginOpt = { mode: items.pluginMode, list: items.pluginWhitelist };
    }
  );
}

loadStorageValue().then(() => {
  console.log("Succesfully load config.")
})

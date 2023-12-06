let nonceMap = {};
let allowOrigin = {};

let keyPair = [];
let pluginOpt = [];
let verifyMap = {};

function str2ab(str) {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

async function importPublicKey(pem) {
  const arrayBuffer = window.atob(pem);
  // convert from a binary string to an ArrayBuffer
  const binaryDer = str2ab(arrayBuffer);
  return window.crypto.subtle.importKey(
    "spki",
    binaryDer,
    {
      name: "ECDSA",
      namedCurve: 'P-256'
    },
    true,
    ["verify"]
  );
}

function b642ab(base64_string) {
  return Uint8Array.from(window.atob(base64_string), c => c.charCodeAt(0));
}

async function verifySignature(signature, public_key, dataStr) {
  var dataBuf = new TextEncoder().encode(dataStr)

  return window.crypto.subtle.verify(
    {
      name: "ECDSA",
      namedCurve: "P-256",
      hash: { name: "SHA-256" },
    },
    public_key,
    b642ab(signature),
    dataBuf
  );
}

const publicKey = `
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOlUz2bUCHQxoVE6x5qwq/a/y/yTabDna/WXKQ6s2SB8dmQo3267COzekI3ZGZ0flTdFo1sxvdPmr1UnmTVCcew==
`


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
              redirectUrl:
                chrome.extension.getURL('hello.html')
            };
          }
        } else if (urlObj.searchParams.get('msafebrowsing_access_token') === "ECDSA") {
          const signature = urlObj.searchParams.get('msafebrowsing_ecdsa_token');
          urlObj.searchParams.delete('msafebrowsing_access_token');
          urlObj.searchParams.delete('msafebrowsing_ecdsa_token');
          // if (verifyMap[signature] === true) {
          //   verifyMap[signature] = false;
          //   allowOrigin[origin] = Date.now(); // allow website access once signature pass
          //   return {
          //     redirectUrl: urlObj.href
          //   };
          // } else 
          {
            verifyMap[signature] = origin;
            console.log("new vmap " + JSON.stringify(verifyMap));
            verifySignature(signature, keyPair[0], urlObj.href + "Benign").then((result) => {
              nonceMap[origin] = undefined;
              if (result) {
                allowOrigin[verifyMap[signature]] = Date.now(); // allow website access once signature pass
                verifyMap[signature] = undefined;
                console.log("new amap " + JSON.stringify(allowOrigin));
              } else {
                alert("Forged malicious website access detected : " + urlObj.href);
              }
            });
            return {
              redirectUrl:
                chrome.extension.getURL('cryptoHandler.html?url='
                  + encodeURIComponent(urlObj.href)
                  + "&msafebrowsing_ecdsa_token="
                  + encodeURIComponent(signature))
            };
          }
        }
      }
      urlObj.searchParams.delete('msafebrowsing_access_token');
      const nonce = generateNonce(); // Function to generate a unique nonce
      nonceMap[origin] = nonce;
      // Redirect to a local handler that will do the check and then redirect accordingly
      return {
        redirectUrl:
          chrome.extension.getURL('localHandler.html?url='
            + encodeURIComponent(urlObj.href)
            + "&token="
            + encodeURIComponent(nonce))
      };
    }
    return { cancel: false };
  },
  { urls: ["*://*/*"] },
  ["blocking"]
);

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

importPublicKey(publicKey).then((pubKey) => {
  keyPair = [pubKey];
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


chrome.storage.sync.onChanged.addListener(() => {
  loadStorageValue().then(() => {
    console.log("Succesfully reloaded config.")
  })
});
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

importPublicKey(publicKey).then((pubKey) => {
    const url = new URL(window.location.href);
    const token = decodeURIComponent(url.searchParams.get('msafebrowsing_ecdsa_token'));
    const gotoToken = decodeURIComponent(url.searchParams.get('url'));
    url.searchParams.delete('msafebrowsing_ecdsa_token', token);
    // verifySignature(signature, pubKey, "https://google.com/Malicious").then((result) => {
    //     console.log(result);
    // })

    document.getElementById("divShowUrl").innerText = gotoToken;

    setTimeout(() => {
        window.location.href = gotoToken; // Navigates to the modified URL
    }, 3000);
})

function addToTrusted() {
    const url = new URL(window.location.href);
    const gotoToken = decodeURIComponent(url.searchParams.get('url'));
    chrome.storage.sync.get(
        { pluginWhitelist: "*://*.google.com/*;\nhttps://*.youtube.com/*" },
        (items) => {
            let separator = '';
            if (! /.*;\s*$/.test(items.pluginWhitelist)) {
                separator += ';\n'
            }
            chrome.storage.sync.set(
                { pluginWhitelist: items.pluginWhitelist + separator + gotoToken.replace(';', '%3B') + '*' },
                () => {
                    // Update status to let user know options were saved.
                    const status = document.getElementById('proceedButton');
                    status.textContent = 'Options saved.';
                    status.disabled = true;
                }
            );
        }
    );
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('proceedButton').addEventListener('click', addToTrusted);
});

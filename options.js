// Saves options to chrome.storage
const saveOptions = () => {
    const mode = document.getElementById('mode').value;
    const whitelist = document.getElementById('whitelist').value;
    const expiry = document.getElementById('expiryTime').value;
  
    chrome.storage.sync.set(
      { pluginMode: mode, pluginWhitelist: whitelist, pluginExpiry: expiry },
      () => {
        // Update status to let user know options were saved.
        const status = document.getElementById('status');
        status.textContent = 'Options saved.';
        setTimeout(() => {
          status.textContent = '';
        }, 750);
      }
    );
  };
  
  // Restores select box and checkbox state using the preferences
  // stored in chrome.storage.
  const restoreOptions = () => {
    chrome.storage.sync.get(
      { pluginMode: 'enabled', pluginWhitelist: "*://*.google.com/*;\nhttps://*.youtube.com/*", pluginExpiry: '43200' },
      (items) => {
        document.getElementById('mode').value = items.pluginMode;
        document.getElementById('whitelist').value = items.pluginWhitelist;
        document.getElementById('expiryTime').value = items.pluginExpiry;
      }
    );
  };
  
  document.addEventListener('DOMContentLoaded', restoreOptions);
  document.getElementById('save').addEventListener('click', saveOptions);
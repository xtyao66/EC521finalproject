// Saves options to chrome.storage
const saveOptions = () => {
    const mode = document.getElementById('mode').value;
    const whitelist = document.getElementById('whitelist').value;
  
    chrome.storage.sync.set(
      { pluginMode: mode, pluginWhitelist: whitelist },
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
      { pluginMode: 'enabled', pluginWhitelist: "*://*.google.com/*;\nhttps://*.youtube.com/*" },
      (items) => {
        document.getElementById('mode').value = items.pluginMode;
        document.getElementById('whitelist').value = items.pluginWhitelist;
      }
    );
  };
  
  document.addEventListener('DOMContentLoaded', restoreOptions);
  document.getElementById('save').addEventListener('click', saveOptions);
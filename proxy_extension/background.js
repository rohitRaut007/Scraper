chrome.runtime.onInstalled.addListener(function () {
  chrome.proxy.settings.set(
    { value: { mode: "fixed_servers", rules: { singleProxy: { scheme: "http", host: "proxy.scraperapi.com", port: 8001 } } }, scope: "regular" },
    function () {}
  );
});

chrome.webRequest.onAuthRequired.addListener(
  function (details, callbackFn) {
    callbackFn({ authCredentials: { username: "scraperapi", password: "YOUR_SCRAPERAPI_KEY" } });
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

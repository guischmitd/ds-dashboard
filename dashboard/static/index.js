
// Not currently loaded, just a template
document.getElementById("refresh-btn").addEventListener("click", RefreshMarketData, false);

function RefreshMarketData() {
    console.log("Refresh triggered!");
    fetch('/refresh').then(response => response.json()).then(function (data) {
        console.log(data);
        document.getElementById("last-updated-text").textContent = data.lastUpdated
    });
}

let x = 60;
// Get new data every x seconds
setInterval(() => {
    RefreshMarketData();
}, x * 1000);


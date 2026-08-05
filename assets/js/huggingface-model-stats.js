(function () {
  "use strict";

  function formatNumber(value) {
    return Number(value).toLocaleString("en-US");
  }

  function updateCard(card) {
    var modelId = card.getAttribute("data-hf-model");

    if (!modelId || !window.fetch) {
      return;
    }

    var encodedModelId = modelId.split("/").map(encodeURIComponent).join("/");

    window.fetch("https://huggingface.co/api/models/" + encodedModelId, {
      headers: { Accept: "application/json" }
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Unable to retrieve model statistics.");
        }
        return response.json();
      })
      .then(function (model) {
        var downloads = card.querySelector("[data-hf-stat='downloads']");
        var likes = card.querySelector("[data-hf-stat='likes']");

        if (typeof model.downloads === "number" && downloads) {
          downloads.textContent = formatNumber(model.downloads);
        }
        if (typeof model.likes === "number" && likes) {
          likes.textContent = formatNumber(model.likes);
        }
      })
      .catch(function () {
        // Keep the server-rendered snapshot available for offline and privacy-restricted visits.
      });
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-hf-model]"), updateCard);
}());

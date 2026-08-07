(function () {
  "use strict";

  function formatNumber(value) {
    return Number(value).toLocaleString("en-US");
  }

  function fetchJson(url) {
    return window.fetch(url, {
      headers: { Accept: "application/json" }
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("Unable to retrieve model statistics.");
      }
      return response.json();
    });
  }

  function updateCard(card) {
    var modelId = card.getAttribute("data-hf-model");

    if (!modelId || !window.fetch) {
      return;
    }

    var encodedModelId = modelId.split("/").map(encodeURIComponent).join("/");

    var modelRequest = fetchJson(
      "https://huggingface.co/api/models/" + encodedModelId + "?expand=downloadsAllTime&expand=likes"
    );
    var derivedModelsRequest = fetchJson(
      "https://huggingface.co/api/models?filter=" +
        encodeURIComponent("base_model:" + modelId) +
        "&expand=downloadsAllTime&limit=1000"
    ).catch(function () {
      return null;
    });

    Promise.all([modelRequest, derivedModelsRequest])
      .then(function (results) {
        var model = results[0];
        var derivedModels = results[1];
        var downloads = card.querySelector("[data-hf-stat='downloads-all-time']");
        var ecosystemDownloads = card.querySelector("[data-hf-stat='ecosystem-downloads-all-time']");
        var likes = card.querySelector("[data-hf-stat='likes']");

        if (typeof model.downloadsAllTime === "number" && downloads) {
          downloads.textContent = formatNumber(model.downloadsAllTime);
        }
        if (
          typeof model.downloadsAllTime === "number" &&
          Array.isArray(derivedModels) &&
          ecosystemDownloads
        ) {
          var totalDownloads = derivedModels.reduce(function (total, derivedModel) {
            return total + (typeof derivedModel.downloadsAllTime === "number" ? derivedModel.downloadsAllTime : 0);
          }, model.downloadsAllTime);

          ecosystemDownloads.textContent = formatNumber(totalDownloads);
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

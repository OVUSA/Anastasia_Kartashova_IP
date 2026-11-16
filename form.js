/* Contact form: posts to the endpoint set in <form action> (Formspree / Web3Forms)
   and shows the result inline. Texts come from content.json via data-msgs. */
(function () {
  "use strict";

  var form = document.getElementById("cform");
  if (!form) return;

  var msgs = JSON.parse(form.dataset.msgs);
  var button = form.querySelector("button");
  var status = form.querySelector(".fstatus");

  function show(text, isError) {
    status.className = isError ? "fstatus err" : "fstatus";
    status.textContent = text;
  }

  function send() {
    button.disabled = true;
    button.textContent = msgs.sending;

    return fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    })
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          if (!response.ok || data.success === false) throw new Error("rejected");
        });
      })
      .then(function () { show(msgs.success); form.reset(); })
      .catch(function () { show(msgs.error, true); })
      .then(function () {
        button.disabled = false;
        button.textContent = msgs.button;
      });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    show("");

    // A filled honeypot means a bot: pretend success, send nothing.
    if (form.elements._gotcha.value || form.elements.botcheck.checked) {
      show(msgs.success);
      form.reset();
      return;
    }
    // No endpoint configured yet.
    if (!form.getAttribute("action")) {
      show(msgs.error, true);
      return;
    }
    send();
  });
})();

/* ====== Settings to fill in (see the setup guide) ====== */
var SITE = {
  // Paste your MailerLite form action URL here, e.g.
  // "https://assets.mailerlite.com/jsonp/123456/forms/987654321/subscribe"
  signupEndpoint: "",
  social: {
    facebook: "",   // e.g. "https://www.facebook.com/alzheimerslantern"
    instagram: "",
    tiktok: "",
    substack: ""
  }
};
/* ======================================================= */

(function () {
  var root = document.documentElement;

  // Larger text toggle (remembered on this device)
  var ts = document.getElementById("textsize");
  function setBig(on) {
    root.classList.toggle("big", on);
    if (ts) { ts.setAttribute("aria-pressed", on ? "true" : "false"); ts.textContent = on ? "A– Smaller text" : "A+ Larger text"; }
  }
  setBig(root.classList.contains("big"));
  if (ts) ts.addEventListener("click", function () {
    var on = !root.classList.contains("big"); setBig(on);
    try { localStorage.setItem("bigText", on ? "1" : "0"); } catch (e) {}
  });

  // Phone menu
  var mb = document.getElementById("menuBtn"), nav = document.getElementById("mainnav");
  if (mb && nav) mb.addEventListener("click", function () {
    var open = !nav.classList.contains("open"); nav.classList.toggle("open", open); mb.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // Footer year
  var yr = document.getElementById("yr"); if (yr) yr.textContent = new Date().getFullYear();

  // Social links: hide the ones not set up yet
  document.querySelectorAll("[data-social]").forEach(function (a) {
    var url = SITE.social[a.getAttribute("data-social")];
    if (url) { a.href = url; a.target = "_blank"; a.rel = "noopener"; }
    else { a.closest("li").hidden = true; }
  });
  document.querySelectorAll(".social").forEach(function (ul) {
    if (!ul.querySelector("li:not([hidden])")) { var li = document.createElement("li"); li.textContent = "Coming soon: Facebook, Instagram, TikTok and Substack"; li.className = "muted"; ul.appendChild(li); }
  });

  // Friday letter signup
  var form = document.getElementById("signup");
  if (form) form.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = document.getElementById("email").value.trim();
    var name = document.getElementById("fname").value.trim();
    var st = document.getElementById("status");
    var btn = document.getElementById("submitBtn");
    st.hidden = false;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { st.textContent = "Please enter a full email address, like name@example.com."; document.getElementById("email").focus(); return; }
    if (!SITE.signupEndpoint) { st.textContent = "Signups open very soon. Please check back in a day or two."; return; }
    var roles = Array.prototype.map.call(form.querySelectorAll('input[name="role"]:checked'), function (i) { return i.value; }).join(", ");
    var body = new URLSearchParams();
    body.append("fields[email]", email);
    if (name) body.append("fields[name]", name);
    if (roles) body.append("fields[role]", roles);
    body.append("ml-submit", "1"); body.append("anticsrf", "true");
    btn.disabled = true; st.textContent = "Signing you up…";
    fetch(SITE.signupEndpoint, { method: "POST", body: body, mode: "no-cors" })
      .then(function () { form.reset(); st.textContent = "Thank you! Please check your inbox and click the link to confirm. Your free 10 Early Signs Checklist comes with the welcome email."; })
      .catch(function () { st.textContent = "Something went wrong. Please check your internet connection and try again."; })
      .then(function () { btn.disabled = false; });
  });
})();

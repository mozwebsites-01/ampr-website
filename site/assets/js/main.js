/* AMPR — interacções do website */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Sombra no cabeçalho depois de rolar ---------- */
  if ("IntersectionObserver" in window) {
    var sentinel = document.createElement("div");
    var topbarEl = document.querySelector(".topbar");
    sentinel.setAttribute("aria-hidden", "true");
    sentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:" + ((topbarEl ? topbarEl.offsetHeight : 0) + 8) + "px;pointer-events:none";
    document.body.prepend(sentinel);
    new IntersectionObserver(function (entries) {
      doc.classList.toggle("is-stuck", !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* ---------- Menu móvel ---------- */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = doc.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && doc.classList.contains("nav-open")) {
        doc.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
    document.querySelectorAll(".main-nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        doc.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Animações SVG (órbitas) com movimento reduzido ---------- */
  if (reduceMotion) {
    document.querySelectorAll(".orbit-svg").forEach(function (svg) {
      if (svg.pauseAnimations) svg.pauseAnimations();
    });
  }

  /* ---------- Contadores ---------- */
  function runCounter(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var numEl = el.querySelector(".n");
    if (reduceMotion) { numEl.textContent = target; return; }
    var start = null, dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      numEl.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { runCounter(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { cio.observe(c); });
  } else {
    counters.forEach(runCounter);
  }

  /* ---------- Separadores (Actividades) ---------- */
  document.querySelectorAll("[data-tabs]").forEach(function (wrap) {
    var tabs = Array.prototype.slice.call(wrap.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () {
        select(t);
        history.replaceState(null, "", "#" + t.getAttribute("data-hash"));
      });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = null;
        if (k === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (k === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === "Home") n = tabs[0];
        if (k === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var hash = location.hash.replace("#", "");
    var initial = tabs.filter(function (t) { return t.getAttribute("data-hash") === hash; })[0] || tabs[0];
    select(initial);
  });

  /* ---------- Índice lateral activo (O Que Fazemos) ---------- */
  var tocLinks = document.querySelectorAll(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var tio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
          var a = map[en.target.id];
          if (a) a.classList.add("is-active");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) tio.observe(el);
    });
  }

  /* ---------- Assunto pré-seleccionado via ?assunto= ---------- */
  var params = new URLSearchParams(location.search);
  var subject = params.get("assunto");
  var subjectSelect = document.getElementById("c-assunto");
  if (subject && subjectSelect) {
    Array.prototype.forEach.call(subjectSelect.options, function (o) {
      if (o.value.toLowerCase() === subject.toLowerCase()) subjectSelect.value = o.value;
    });
  }

  /* ---------- Formulários ----------
     Para receber as mensagens, preencha data-endpoint no <form> com o URL
     de um serviço de formulários (ex.: Formspree, Getform ou um servidor próprio). */
  function setStatus(box, type, msg) {
    box.className = "form-status is-visible " + type;
    box.textContent = msg;
  }
  function fieldError(field, msg) {
    var wrap = field.closest(".field");
    var err = wrap ? wrap.querySelector(".field-error") : null;
    if (msg) {
      field.setAttribute("aria-invalid", "true");
      if (err) { err.textContent = msg; field.setAttribute("aria-describedby", err.id); }
    } else {
      field.removeAttribute("aria-invalid");
      if (err) err.textContent = "";
    }
  }
  function messageFor(field) {
    var v = field.validity;
    if (v.valueMissing) return field.type === "checkbox" ? "Confirme para continuar." : "Preencha este campo.";
    if (v.typeMismatch && field.type === "email") return "Escreva um e-mail válido, por exemplo nome@dominio.com.";
    if (v.patternMismatch) return field.getAttribute("data-pattern-msg") || "Verifique o formato.";
    return "";
  }

  document.querySelectorAll(".js-form").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.querySelectorAll("input, select, textarea").forEach(function (f) {
      f.addEventListener("blur", function () { if (f.value) fieldError(f, messageFor(f)); });
      f.addEventListener("input", function () { if (f.getAttribute("aria-invalid")) fieldError(f, messageFor(f)); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;
      form.querySelectorAll("input, select, textarea").forEach(function (f) {
        var msg = messageFor(f);
        fieldError(f, msg);
        if (msg && !firstBad) firstBad = f;
      });
      if (firstBad) {
        setStatus(status, "err", "Corrija os campos assinalados a vermelho e envie de novo.");
        firstBad.focus();
        return;
      }
      var endpoint = form.getAttribute("data-endpoint");
      var btn = form.querySelector('[type="submit"]');
      if (!endpoint) {
        setStatus(status, "info", "Este formulário ainda não está ligado a um serviço de envio. Escreva-nos pelos contactos da AMPR.");
        return;
      }
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = "A enviar…";
      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          setStatus(status, "ok", form.getAttribute("data-success") || "Mensagem enviada. Respondemos com a maior brevidade.");
        })
        .catch(function () {
          setStatus(status, "err", "Não foi possível enviar. Verifique a ligação à internet e tente de novo.");
        })
        .then(function () { btn.disabled = false; btn.textContent = label; });
    });
  });
})();

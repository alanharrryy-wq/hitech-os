(function(){
  "use strict";
  const labels = {
    operation: ["CABINA OPERATIVA", "Control Center"],
    quality: ["QUALITY BAY", "Customer Assurance"],
    license: ["LICENCIAS", "Runtime Local-first"],
    lifecycle: ["DATA LIFECYCLE", "Data Registry"],
    prismo: ["PRISMO", "Gemini Command Nexus"]
  };
  function apply(){
    const key = document.body && document.body.dataset ? document.body.dataset.prismaInterface : "";
    const pair = labels[key];
    if(!pair) return;
    const h1 = document.querySelector(".topbar .titles h1");
    const sub = document.querySelector("#subtitle, .topbar .titles p");
    if(h1) h1.textContent = pair[0];
    if(sub) sub.textContent = pair[1];
  }
  document.addEventListener("click", function(e){
    const b = e.target && e.target.closest ? e.target.closest("[data-prisma-interface-target]") : null;
    if(b) setTimeout(apply, 30);
  }, true);
  setInterval(apply, 800);
  apply();
})();

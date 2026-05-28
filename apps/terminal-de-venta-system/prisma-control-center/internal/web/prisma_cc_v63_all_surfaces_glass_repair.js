(function(){
  "use strict";
  const labels = {
    operation: ["CABINA OPERATIVA", "Control Center"],
    quality: ["PRISMA QUALITY BAY", "Customer Assurance Console"],
    license: ["PRISMA LICENCIAS", "Runtime Local-first"],
    lifecycle: ["CONTROL CENTER", "Data Lifecycle"],
    prismo: ["PRISMO", "Gemini Command Nexus"]
  };
  function apply(){
    const key = document.body && document.body.dataset ? document.body.dataset.prismaInterface : "";
    const pair = labels[key];
    if(!pair) return;
    const h1 = document.querySelector(".topbar .titles h1");
    const sub = document.querySelector("#subtitle, .topbar .titles p");
    if(h1 && h1.textContent.trim() !== pair[0]) h1.textContent = pair[0];
    if(sub && sub.textContent.trim() !== pair[1]) sub.textContent = pair[1];
  }
  document.addEventListener("click", function(e){
    const b = e.target && e.target.closest ? e.target.closest("[data-prisma-interface-target]") : null;
    if(b) setTimeout(apply, 40);
  }, true);
  setInterval(apply, 700);
  apply();
})();

(function(){
  "use strict";
  const labels = {
    operation:["CABINA OPERATIVA","Control Center · reactor, rutas, señales y evidencia"],
    quality:["QUALITY BAY","Customer Assurance · soporte, upgrade y evidencia"],
    license:["LICENCIAS","Runtime local-first · identidad y provisioning"],
    lifecycle:["DATA LIFECYCLE","Data registry · limpieza, PIN, evidencia y rollback"]
  };
  function apply(){
    const key=document.body && document.body.dataset ? document.body.dataset.prismaInterface : "";
    const pair=labels[key];
    if(!pair) return;
    const h1=document.querySelector(".topbar .titles h1");
    const sub=document.querySelector("#subtitle, .topbar .titles p");
    const logo=document.querySelector(".topbar .heroLogo");
    if(h1) h1.textContent=pair[0];
    if(sub) sub.textContent=pair[1];
    if(logo){
      logo.style.opacity="1";
      logo.style.visibility="visible";
    }
  }
  document.addEventListener("click",function(e){
    const b=e.target && e.target.closest ? e.target.closest("[data-prisma-interface-target]") : null;
    if(b) setTimeout(apply,40);
  },true);
  setInterval(apply,900);
  apply();
})();

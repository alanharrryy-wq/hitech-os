(function(){
  "use strict";
  function fix(){
    if(document.body.dataset.prismaInterface !== "prismo") return;
    var title=document.querySelector(".topbar .titles h1");
    var subtitle=document.querySelector("#subtitle");
    if(title) title.textContent="PRISMO";
    if(subtitle) subtitle.textContent="Gemini Command Nexus";
  }
  document.addEventListener("click",function(e){
    var b=e.target && e.target.closest ? e.target.closest('[data-prisma-interface-target="prismo"]') : null;
    if(b) setTimeout(fix,0);
  },true);
  setInterval(fix,500);
  fix();
})();

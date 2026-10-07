const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('#main-nav');
if(toggle&&nav){toggle.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));});nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');toggle.setAttribute('aria-expanded','false');}));}

const THEME_KEY='tlumacz-theme';
const themeButton=document.querySelector('.theme-toggle');
const themeLabel=document.querySelector('.theme-label');
const themes=['system','light','dark'];

function applyTheme(theme){
  const value=themes.includes(theme)?theme:'system';
  document.documentElement.dataset.theme=value;
  document.documentElement.style.colorScheme=value==='system'?'light dark':value;
  if(themeLabel) themeLabel.textContent=value==='light'?'Jasny':value==='dark'?'Ciemny':'Systemowy';
  if(themeButton){
    themeButton.setAttribute('aria-label',`Motyw: ${value}. Zmień motyw`);
    themeButton.setAttribute('title',`Motyw: ${value}. Zmień motyw`);
  }
}

const savedTheme=localStorage.getItem(THEME_KEY);
applyTheme(savedTheme||'system');
if(themeButton){
  themeButton.addEventListener('click',()=>{
    const current=document.documentElement.dataset.theme||'system';
    const next=themes[(themes.indexOf(current)+1)%themes.length];
    localStorage.setItem(THEME_KEY,next);
    applyTheme(next);
  });
}

const year=document.querySelector('#year'); if(year) year.textContent=new Date().getFullYear();

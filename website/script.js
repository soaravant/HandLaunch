(function(){
  const $ = (sel)=>document.querySelector(sel);
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  const os = detectOS();
  const note = $('#detected-os-note');
  if (note) note.textContent = os ? `Detected: ${osLabel(os)}` : '';

  highlightDownload(os);
  rewritePrimaryCTA(os);

  function detectOS(){
    const ua = navigator.userAgent || navigator.platform || '';
    const p = navigator.platform || '';
    if (/Mac|iPhone|iPad|iPod/.test(p) || /Mac OS X/.test(ua)) return 'macos';
    if (/Win/.test(p) || /Windows/.test(ua)) return 'windows';
    if (/Linux|X11|Ubuntu|Fedora|Manjaro|Arch|Debian|CentOS/.test(ua)) return 'linux';
    return null;
  }

  function osLabel(os){
    switch(os){
      case 'macos': return 'macOS';
      case 'windows': return 'Windows';
      case 'linux': return 'Linux';
      default: return '';
    }
  }

  function highlightDownload(os){
    const cards = document.querySelectorAll('.download-card');
    cards.forEach(c=>c.classList.remove('active'));
    if (!os) return;
    const el = document.querySelector(`.download-card[data-os="${os}"]`);
    if (el) el.classList.add('active');
  }

  function rewritePrimaryCTA(os){
    const btn = $('#primary-download');
    if (!btn || !os) return;
    const map = {
      macos: 'https://github.com/soaravant/HandLaunch/releases/latest/download/HandLaunch-mac.zip',
      windows: 'https://github.com/soaravant/HandLaunch/releases/latest/download/HandLaunch-win.exe',
      linux: 'https://github.com/soaravant/HandLaunch/releases/latest/download/HandLaunch-linux.tar.gz'
    };
    btn.href = map[os];
  }
})();



(function(){
  const $ = (sel)=>document.querySelector(sel);
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  const os = detectOS();
  const note = $('#detected-os-note');
  if (note) note.textContent = os ? `Detected: ${osLabel(os)}` : '';

  highlightDownload(os);
  rewritePrimaryCTA(os);
  updateAppPreviews(os);
  startGestureAnimation();

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

  function updateAppPreviews(os){
    const appMappings = {
      macos: {
        open_palm: { name: "Safari", icon: "/assets/icons/safari.png" },
        fist: { name: "Finder", icon: "/assets/icons/finder.png" },
        peace_sign: { name: "TextEdit", icon: "/assets/icons/textedit.png" },
        thumbs_up: { name: "Mail", icon: "/assets/icons/mail.png" },
        pointing: { name: "Terminal", icon: "/assets/icons/terminal.png" }
      },
      windows: {
        open_palm: { name: "Chrome", icon: "/assets/icons/chrome.png" },
        fist: { name: "Explorer", icon: "/assets/icons/explorer.png" },
        peace_sign: { name: "Firefox", icon: "/assets/icons/firefox.png" },
        thumbs_up: { name: "Notepad", icon: "/assets/icons/notepad.png" },
        pointing: { name: "Windows Media Player", icon: "/assets/icons/wmp.png" }
      },
      linux: {
        open_palm: { name: "Firefox", icon: "/assets/icons/firefox.png" },
        fist: { name: "Nautilus", icon: "/assets/icons/nautilus.png" },
        peace_sign: { name: "Chrome", icon: "/assets/icons/chrome.png" },
        thumbs_up: { name: "VLC", icon: "/assets/icons/vlc.png" },
        pointing: { name: "Gedit", icon: "/assets/icons/gedit.png" }
      }
    };

    const apps = appMappings[os] || appMappings.macos;
    
    Object.keys(apps).forEach(gesture => {
      const app = apps[gesture];
      const iconEl = document.getElementById(`${gesture.replace('_', '-')}-app`);
      const nameEl = document.getElementById(`${gesture.replace('_', '-')}-name`);
      
      if (iconEl) {
        const img = document.createElement('img');
        img.src = app.icon;
        img.alt = app.name;
        img.style.width = '20px';
        img.style.height = '20px';
        img.onload = function() {
          console.log('Icon loaded successfully:', app.icon);
        };
        img.onerror = function() {
          console.error('Failed to load icon:', app.icon);
          // Fallback to a generic app icon if the specific icon fails to load
          this.style.display = 'none';
          iconEl.innerHTML = '<div style="width: 20px; height: 20px; background: #666; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white;">📱</div>';
        };
        iconEl.innerHTML = '';
        iconEl.appendChild(img);
      }
      if (nameEl) nameEl.textContent = app.name;
    });
  }

  function startGestureAnimation(){
    const cards = document.querySelectorAll('.gesture-card');
    if (!cards.length) return;
    
    let currentIndex = 0;
    
    function showNextCard(){
      cards.forEach(card => card.classList.remove('active'));
      cards[currentIndex].classList.add('active');
      currentIndex = (currentIndex + 1) % cards.length;
    }
    
    // Start with first card
    showNextCard();
    
    // Cycle every 2 seconds
    setInterval(showNextCard, 2000);
  }

  // Initialize tech canvas
  initTechCanvas();
})();

function initTechCanvas() {
  const canvas = document.getElementById('tech-canvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  let scale = 1;
  let offsetX = 0;
  let offsetY = 0;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let hoveredNode = null;
  let selectedNode = null;
  const detailsEl = document.getElementById('node-details');
  const detailsTitle = detailsEl?.querySelector('.node-title');
  const detailsDesc = detailsEl?.querySelector('.node-desc');

  // Technology nodes data - reorganized with better spacing
  const techNodes = [
    {
      id: 'python',
      name: 'Python',
      category: 'language',
      x: 400, y: 300,
      color: '#3776ab',
      description: 'The foundation of HandLaunch. Python orchestrates the entire gesture recognition pipeline, from camera capture to app launching. It provides the runtime environment that binds all components together, ensuring cross-platform compatibility and enabling rapid development of the gesture detection algorithms.',
      connections: ['opencv', 'mediapipe', 'pyqt5', 'numpy', 'tensorflow']
    },
    {
      id: 'opencv',
      name: 'OpenCV',
      category: 'computer-vision',
      x: 150, y: 150,
      color: '#5c3ee8',
      description: 'The eyes of HandLaunch. OpenCV handles real-time camera feed processing, image preprocessing, and computer vision operations. It captures frames from your webcam, applies noise reduction and enhancement filters, and prepares the visual data for gesture analysis. Essential for maintaining consistent image quality across different lighting conditions.',
      connections: ['python', 'mediapipe', 'numpy']
    },
    {
      id: 'mediapipe',
      name: 'MediaPipe',
      category: 'ml',
      x: 300, y: 100,
      color: '#4285f4',
      description: 'The brain of gesture recognition. MediaPipe\'s hand landmark detection identifies 21 key points on each hand in real-time. It transforms raw camera frames into structured hand pose data, enabling precise gesture classification. This is where your hand movements become actionable commands that the system can understand and respond to.',
      connections: ['python', 'opencv', 'tensorflow']
    },
    {
      id: 'pyqt5',
      name: 'PyQt5',
      category: 'gui',
      x: 650, y: 200,
      color: '#41cd52',
      description: 'The user interface layer. PyQt5 creates the intuitive desktop application where users configure gesture mappings, train custom gestures, and monitor the system. It provides the settings panel, gesture trainer, and real-time camera preview, making HandLaunch accessible to users without technical expertise.',
      connections: ['python']
    },
    {
      id: 'tensorflow',
      name: 'TensorFlow',
      category: 'ml',
      x: 200, y: 400,
      color: '#ff6f00',
      description: 'The machine learning engine. TensorFlow powers the gesture classification models that distinguish between different hand poses. It processes the hand landmarks from MediaPipe and determines whether you\'re showing a fist, open palm, peace sign, or other gestures. The models run entirely on-device for privacy and speed.',
      connections: ['python', 'mediapipe', 'numpy']
    },
    {
      id: 'numpy',
      name: 'NumPy',
      category: 'data',
      x: 100, y: 300,
      color: '#4dabcf',
      description: 'The mathematical backbone. NumPy handles all numerical computations, from processing hand landmark coordinates to calculating gesture similarity scores. It provides efficient array operations for real-time data processing, ensuring smooth performance even with complex gesture recognition algorithms running at 30+ FPS.',
      connections: ['python', 'opencv', 'tensorflow']
    },
    {
      id: 'scikit-learn',
      name: 'Scikit-learn',
      category: 'ml',
      x: 300, y: 500,
      color: '#f7931e',
      description: 'The gesture learning system. Scikit-learn enables users to train custom gestures by learning from their unique hand movements. It uses machine learning algorithms to create personalized gesture models, adapting to individual variations in hand shape and movement patterns for more accurate recognition.',
      connections: ['python', 'numpy']
    },
    {
      id: 'pillow',
      name: 'Pillow',
      category: 'image',
      x: 500, y: 400,
      color: '#f7b731',
      description: 'The image processing toolkit. Pillow handles icon and image manipulation for the user interface, processes gesture training data, and manages visual assets. It ensures consistent image quality and format compatibility across different operating systems, contributing to the polished user experience.',
      connections: ['python', 'opencv']
    },
    {
      id: 'pyinstaller',
      name: 'PyInstaller',
      category: 'build',
      x: 700, y: 400,
      color: '#9b59b6',
      description: 'The deployment architect. PyInstaller packages the entire HandLaunch application into standalone executables for macOS, Windows, and Linux. It bundles all dependencies, models, and resources into a single distributable file, making HandLaunch easy to install and run without requiring Python or complex setup procedures.',
      connections: ['python']
    },
    {
      id: 'psutil',
      name: 'psutil',
      category: 'system',
      x: 600, y: 500,
      color: '#e74c3c',
      description: 'The system integration layer. psutil enables HandLaunch to interact with the operating system, launching applications, monitoring system resources, and managing processes. It provides the bridge between gesture recognition and actual app launching, ensuring reliable cross-platform application management.',
      connections: ['python']
    }
  ];

  // Grouping boxes for organizing components
  const groupBoxes = [
    {
      title: 'Computer Vision & ML',
      x: 50, y: 50,
      width: 350, height: 200,
      color: 'rgba(66, 133, 244, 0.1)',
      borderColor: 'rgba(66, 133, 244, 0.3)',
      nodes: ['opencv', 'mediapipe', 'tensorflow', 'numpy']
    },
    {
      title: 'User Interface',
      x: 600, y: 150,
      width: 200, height: 100,
      color: 'rgba(65, 205, 82, 0.1)',
      borderColor: 'rgba(65, 205, 82, 0.3)',
      nodes: ['pyqt5']
    },
    {
      title: 'Core Runtime',
      x: 350, y: 250,
      width: 150, height: 100,
      color: 'rgba(55, 118, 171, 0.1)',
      borderColor: 'rgba(55, 118, 171, 0.3)',
      nodes: ['python']
    },
    {
      title: 'Training & Learning',
      x: 250, y: 450,
      width: 200, height: 100,
      color: 'rgba(247, 147, 30, 0.1)',
      borderColor: 'rgba(247, 147, 30, 0.3)',
      nodes: ['scikit-learn']
    },
    {
      title: 'System Integration',
      x: 450, y: 350,
      width: 300, height: 200,
      color: 'rgba(231, 76, 60, 0.1)',
      borderColor: 'rgba(231, 76, 60, 0.3)',
      nodes: ['pillow', 'pyinstaller', 'psutil']
    }
  ];

  // Event listeners
  canvas.addEventListener('mousedown', handleMouseDown);
  canvas.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseup', handleMouseUp);
  canvas.addEventListener('wheel', handleWheel);
  canvas.addEventListener('click', handleClick);

  // Control buttons
  document.getElementById('zoom-in')?.addEventListener('click', () => zoom(1.2));
  document.getElementById('zoom-out')?.addEventListener('click', () => zoom(0.8));
  document.getElementById('reset-view')?.addEventListener('click', resetView);

  function handleMouseDown(e) {
    isDragging = true;
    dragStartX = e.clientX - offsetX;
    dragStartY = e.clientY - offsetY;
    canvas.style.cursor = 'grabbing';
  }

  function handleMouseMove(e) {
    if (isDragging) {
      offsetX = e.clientX - dragStartX;
      offsetY = e.clientY - dragStartY;
      draw();
    } else {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left - offsetX) / scale;
      const y = (e.clientY - rect.top - offsetY) / scale;
      
      const node = getNodeAt(x, y);
      if (node !== hoveredNode) {
        hoveredNode = node;
        canvas.style.cursor = node ? 'pointer' : 'grab';
        draw();
      }
    }
  }

  function handleMouseUp() {
    isDragging = false;
    canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  }

  function handleWheel(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    zoom(zoomFactor, mouseX, mouseY);
  }

  function handleClick(e) {
    if (isDragging) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - offsetX) / scale;
    const y = (e.clientY - rect.top - offsetY) / scale;
    
    const node = getNodeAt(x, y);
    if (node) {
      selectedNode = selectedNode === node ? null : node;
      draw();
      
      // Show node details panel
      if (selectedNode && detailsEl && detailsTitle && detailsDesc) {
        detailsEl.classList.remove('hidden');
        detailsTitle.textContent = selectedNode.name;
        detailsDesc.textContent = selectedNode.description;
      } else if (detailsEl) {
        detailsEl.classList.add('hidden');
      }
    }
  }

  function zoom(factor, centerX = canvas.width / 2, centerY = canvas.height / 2) {
    const newScale = Math.max(0.3, Math.min(3, scale * factor));
    const scaleChange = newScale / scale;
    
    offsetX = centerX - (centerX - offsetX) * scaleChange;
    offsetY = centerY - (centerY - offsetY) * scaleChange;
    scale = newScale;
    
    draw();
  }

  function resetView() {
    scale = 1;
    offsetX = 0;
    offsetY = 0;
    selectedNode = null;
    draw();
  }

  function getNodeAt(x, y) {
    for (let node of techNodes) {
      const w = 140; // node width
      const h = 56;  // node height
      const left = node.x - w/2;
      const top = node.y - h/2;
      if (x >= left && x <= left + w && y >= top && y <= top + h) return node;
    }
    return null;
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    // Draw grouping boxes first (behind everything)
    for (let box of groupBoxes) {
      // Draw box background
      ctx.fillStyle = box.color;
      ctx.fillRect(box.x, box.y, box.width, box.height);
      
      // Draw box border
      ctx.strokeStyle = box.borderColor;
      ctx.lineWidth = 2;
      ctx.strokeRect(box.x, box.y, box.width, box.height);
      
      // Draw box title
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.font = 'bold 12px system-ui, -apple-system, sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(box.title, box.x + 8, box.y + 8);
    }

    // Draw rectangular connections with corners
    ctx.strokeStyle = 'rgba(77, 124, 255, 0.5)';
    ctx.lineWidth = 2;
    for (let node of techNodes) {
      for (let connectionId of node.connections) {
        const targetNode = techNodes.find(n => n.id === connectionId);
        if (targetNode) {
          drawRectangularConnection(node, targetNode);
        }
      }
    }

    // Draw nodes as rounded rectangles with a circular emoji icon
    for (let node of techNodes) {
      const isHovered = hoveredNode === node;
      const isSelected = selectedNode === node;
      const w = 140; const h = 56; const r = 12; // rect dims + corner radius
      const x = node.x - w/2; const y = node.y - h/2;

      // Rect background
      ctx.beginPath();
      roundedRect(ctx, x, y, w, h, r);
      ctx.fillStyle = isSelected ? shade(node.color, 0.0) : isHovered ? shade(node.color, 0.1) : node.color;
      ctx.fill();

      // Rect border
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeStyle = isSelected ? '#ffffff' : isHovered ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)';
      ctx.stroke();

      // Circular icon container
      const iconR = 18;
      const iconCx = x + 22 + iconR;
      const iconCy = node.y;
      ctx.beginPath();
      ctx.arc(iconCx, iconCy, iconR, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fill();

      // Emoji icon representing category
      const catEmoji = {
        'language':'🐍',
        'computer-vision':'📷',
        'ml':'🤖',
        'gui':'🖼️',
        'data':'🧮',
        'image':'🖼️',
        'build':'📦',
        'system':'⚙️'
      }[node.category] || '🔧';
      ctx.font = '18px Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, system-ui';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(catEmoji, iconCx, iconCy+1);

      // Node name text
      ctx.fillStyle = '#ffffff';
      ctx.font = `${isHovered || isSelected ? 'bold 12px' : '11px'} system-ui, -apple-system, sans-serif`;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, x + 22 + iconR*2 + 10, node.y);
    }

    ctx.restore();
  }

  // Helper: draw rectangular connection with corners
  function drawRectangularConnection(sourceNode, targetNode) {
    const dx = targetNode.x - sourceNode.x;
    const dy = targetNode.y - sourceNode.y;
    const absDx = Math.abs(dx);
    const absDy = Math.abs(dy);
    
    // Determine connection style based on distance and direction
    let path = [];
    
    if (absDx > absDy) {
      // Horizontal connection with vertical offset
      const midX = sourceNode.x + dx / 2;
      const offsetY = dy > 0 ? 30 : -30;
      
      path = [
        { x: sourceNode.x, y: sourceNode.y },
        { x: midX, y: sourceNode.y },
        { x: midX, y: sourceNode.y + offsetY },
        { x: midX, y: targetNode.y - offsetY },
        { x: midX, y: targetNode.y },
        { x: targetNode.x, y: targetNode.y }
      ];
    } else {
      // Vertical connection with horizontal offset
      const midY = sourceNode.y + dy / 2;
      const offsetX = dx > 0 ? 30 : -30;
      
      path = [
        { x: sourceNode.x, y: sourceNode.y },
        { x: sourceNode.x, y: midY },
        { x: sourceNode.x + offsetX, y: midY },
        { x: targetNode.x - offsetX, y: midY },
        { x: targetNode.x, y: midY },
        { x: targetNode.x, y: targetNode.y }
      ];
    }
    
    // Draw the path
    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);
    for (let i = 1; i < path.length; i++) {
      ctx.lineTo(path[i].x, path[i].y);
    }
    ctx.stroke();
    
    // Draw arrow at the end
    const lastPoint = path[path.length - 1];
    const secondLastPoint = path[path.length - 2];
    const angle = Math.atan2(lastPoint.y - secondLastPoint.y, lastPoint.x - secondLastPoint.x);
    const arrowLength = 8;
    const arrowAngle = Math.PI / 6;
    
    ctx.beginPath();
    ctx.moveTo(lastPoint.x, lastPoint.y);
    ctx.lineTo(
      lastPoint.x - arrowLength * Math.cos(angle - arrowAngle),
      lastPoint.y - arrowLength * Math.sin(angle - arrowAngle)
    );
    ctx.moveTo(lastPoint.x, lastPoint.y);
    ctx.lineTo(
      lastPoint.x - arrowLength * Math.cos(angle + arrowAngle),
      lastPoint.y - arrowLength * Math.sin(angle + arrowAngle)
    );
    ctx.stroke();
  }

  // Helper: rounded rectangle path
  function roundedRect(ctx, x, y, w, h, r){
    ctx.moveTo(x+r, y);
    ctx.arcTo(x+w, y, x+w, y+h, r);
    ctx.arcTo(x+w, y+h, x, y+h, r);
    ctx.arcTo(x, y+h, x, y, r);
    ctx.arcTo(x, y, x+w, y, r);
    ctx.closePath();
  }

  // Helper: shade color slightly (expects hex #rrggbb)
  function shade(hex, amt){
    try{
      const c = hex.startsWith('#') ? hex.slice(1) : hex;
      const num = parseInt(c, 16);
      const r = Math.min(255, Math.max(0, (num >> 16) + Math.round(255*amt)));
      const g = Math.min(255, Math.max(0, ((num >> 8) & 0xff) + Math.round(255*amt)));
      const b = Math.min(255, Math.max(0, (num & 0xff) + Math.round(255*amt)));
      return `#${(r<<16 | g<<8 | b).toString(16).padStart(6,'0')}`;
    }catch{ return hex; }
  }

  // Initial draw
  draw();
}



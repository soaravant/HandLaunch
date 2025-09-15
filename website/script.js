(function(){
  const $ = (sel)=>document.querySelector(sel);
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  const os = detectOS();
  const note = $('#detected-os-note');
  if (note) note.textContent = os ? `Detected: ${osLabel(os)}` : '';

  highlightCommand(os);
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

  function highlightCommand(os){
    const cards = document.querySelectorAll('.command-card');
    cards.forEach(c=>c.classList.remove('active'));
    if (!os) return;
    const el = document.querySelector(`.command-card[data-os="${os}"]`);
    if (el) el.classList.add('active');
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
      // Map gesture names to correct HTML IDs
      const idMap = {
        'open_palm': 'open-palm',
        'fist': 'fist', 
        'peace_sign': 'peace',
        'thumbs_up': 'thumbs',
        'pointing': 'pointing'
      };
      const gestureId = idMap[gesture] || gesture.replace('_', '-');
      const iconEl = document.getElementById(`${gestureId}-app`);
      const nameEl = document.getElementById(`${gestureId}-name`);
      
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

// Copy command function
function copyCommand(commandId) {
  // Define the actual commands
  const commands = {
    'macos-command': 'git clone https://github.com/soaravant/HandLaunch.git && cd HandLaunch && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python src/main.py',
    'windows-command': 'git clone https://github.com/soaravant/HandLaunch.git && cd HandLaunch && python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt && python src\\main.py',
    'linux-command': 'git clone https://github.com/soaravant/HandLaunch.git && cd HandLaunch && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python src/main.py'
  };
  
  const commandText = commands[commandId];
  if (!commandText) return;
  
  // Try to use the modern clipboard API first
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(commandText).then(() => {
      const commandElement = document.getElementById(commandId);
      showCopyFeedback(commandElement);
    }).catch(() => {
      const commandElement = document.getElementById(commandId);
      fallbackCopyTextToClipboard(commandText, commandElement);
    });
  } else {
    const commandElement = document.getElementById(commandId);
    fallbackCopyTextToClipboard(commandText, commandElement);
  }
}

function fallbackCopyTextToClipboard(text, element) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  
  try {
    document.execCommand('copy');
    showCopyFeedback(element);
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
  
  document.body.removeChild(textArea);
}

function showCopyFeedback(element) {
  const button = element.parentElement.querySelector('.copy-btn');
  const originalText = button.textContent;
  button.textContent = '✓';
  button.style.background = '#10b981';
  
  setTimeout(() => {
    button.textContent = originalText;
    button.style.background = '';
  }, 2000);
}

function initTechCanvas() {
  const canvas = document.getElementById('tech-canvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  let scale = 0.6; // More zoomed out by default
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
  const categoriesEl = document.getElementById('tech-categories');

  // Category mapping for highlighting
  const categoryMap = {
    'language': 'Core Language',
    'computer-vision': 'Computer Vision', 
    'ml': 'Machine Learning',
    'gui': 'User Interface',
    'data': 'Data Processing',
    'image': 'User Interface',
    'build': 'Build & Deploy',
    'system': 'System Integration'
  };

  // Technology nodes data - reorganized with much better spacing and logical flow
  const techNodes = [
    {
      id: 'python',
      name: 'Python',
      category: 'language',
      x: 600, y: 450,
      color: '#3776ab',
      description: '• Core runtime environment for the entire application\n• Orchestrates the complete gesture recognition pipeline\n• Ensures cross-platform compatibility across macOS, Windows, and Linux\n• Provides the foundation that binds all components together\n• Enables rapid development and testing of gesture detection algorithms',
      connections: ['opencv', 'mediapipe', 'pyqt5', 'numpy', 'tensorflow', 'scikit-learn', 'pillow', 'pyinstaller', 'psutil']
    },
    {
      id: 'opencv',
      name: 'OpenCV',
      category: 'computer-vision',
      x: 200, y: 200,
      color: '#5c3ee8',
      description: '• Real-time camera feed capture and processing\n• Image preprocessing and enhancement filters\n• Noise reduction and lighting condition adaptation\n• Frame rate optimization for smooth performance\n• Cross-platform camera interface management',
      connections: ['python', 'mediapipe', 'numpy']
    },
    {
      id: 'mediapipe',
      name: 'MediaPipe',
      category: 'ml',
      x: 400, y: 150,
      color: '#4285f4',
      description: '• Hand landmark detection with 21 key points per hand\n• Real-time hand pose estimation and tracking\n• Converts camera frames to structured hand data\n• Enables precise gesture classification\n• Optimized for mobile and desktop performance',
      connections: ['python', 'opencv', 'tensorflow']
    },
    {
      id: 'tensorflow',
      name: 'TensorFlow',
      category: 'ml',
      x: 350, y: 650,
      color: '#ff6f00',
      description: '• Machine learning engine for gesture classification\n• Processes hand landmarks to identify gestures\n• Distinguishes between fist, open palm, peace sign, etc.\n• Runs entirely on-device for privacy and speed\n• Supports both training and inference modes',
      connections: ['python', 'mediapipe', 'numpy']
    },
    {
      id: 'numpy',
      name: 'NumPy',
      category: 'data',
      x: 150, y: 450,
      color: '#4dabcf',
      description: '• Mathematical backbone for all computations\n• Handles hand landmark coordinate processing\n• Calculates gesture similarity scores and metrics\n• Efficient array operations for real-time processing\n• Optimized for 30+ FPS performance requirements',
      connections: ['python', 'opencv', 'tensorflow', 'scikit-learn']
    },
    {
      id: 'scikit-learn',
      name: 'Scikit-learn',
      category: 'ml',
      x: 450, y: 750,
      color: '#f7931e',
      description: '• Custom gesture training and learning system\n• Machine learning algorithms for personalized models\n• Adapts to individual hand shape variations\n• Creates user-specific gesture recognition patterns\n• Enables continuous learning and improvement',
      connections: ['python', 'numpy', 'tensorflow']
    },
    {
      id: 'pyqt5',
      name: 'PyQt5',
      category: 'gui',
      x: 950, y: 300,
      color: '#41cd52',
      description: '• Desktop application user interface\n• Gesture mapping configuration panel\n• Real-time camera preview and monitoring\n• Custom gesture training interface\n• Settings and preferences management',
      connections: ['python', 'pillow']
    },
    {
      id: 'pillow',
      name: 'Pillow',
      category: 'image',
      x: 800, y: 550,
      color: '#f7b731',
      description: '• Image processing and manipulation toolkit\n• Icon and visual asset management\n• Gesture training data image processing\n• Cross-platform image format compatibility\n• UI visual enhancement and optimization',
      connections: ['python', 'opencv', 'pyqt5']
    },
    {
      id: 'pyinstaller',
      name: 'PyInstaller',
      category: 'build',
      x: 1000, y: 550,
      color: '#9b59b6',
      description: '• Application packaging and deployment\n• Creates standalone executables for all platforms\n• Bundles all dependencies and resources\n• Generates macOS .dmg, Windows .exe, Linux .AppImage\n• Enables easy installation without Python setup',
      connections: ['python', 'pyqt5']
    },
    {
      id: 'psutil',
      name: 'psutil',
      category: 'system',
      x: 900, y: 700,
      color: '#e74c3c',
      description: '• System integration and process management\n• Application launching and process control\n• System resource monitoring and optimization\n• Cross-platform OS interaction\n• Bridge between gestures and app execution',
      connections: ['python', 'pyqt5']
    }
  ];

  // Grouping boxes for organizing components - updated for better layout with much more spread out nodes
  const groupBoxes = [
    {
      title: 'Computer Vision & ML',
      x: 100, y: 100,
      width: 350, height: 400,
      color: 'rgba(66, 133, 244, 0.1)',
      borderColor: 'rgba(66, 133, 244, 0.3)',
      nodes: ['opencv', 'mediapipe', 'numpy']
    },
    {
      title: 'Core Runtime',
      x: 520, y: 370,
      width: 160, height: 160,
      color: 'rgba(55, 118, 171, 0.1)',
      borderColor: 'rgba(55, 118, 171, 0.3)',
      nodes: ['python']
    },
    {
      title: 'User Interface',
      x: 880, y: 220,
      width: 200, height: 160,
      color: 'rgba(65, 205, 82, 0.1)',
      borderColor: 'rgba(65, 205, 82, 0.3)',
      nodes: ['pyqt5']
    },
    {
      title: 'Training & Learning',
      x: 280, y: 580,
      width: 250, height: 250,
      color: 'rgba(247, 147, 30, 0.1)',
      borderColor: 'rgba(247, 147, 30, 0.3)',
      nodes: ['tensorflow', 'scikit-learn']
    },
    {
      title: 'System Integration',
      x: 720, y: 470,
      width: 400, height: 280,
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
  canvas.addEventListener('mouseleave', () => {
    hoveredNode = null;
    highlightCategory(null);
    draw();
  });

  // Control buttons
  document.getElementById('zoom-in')?.addEventListener('click', () => zoom(1.1));
  document.getElementById('zoom-out')?.addEventListener('click', () => zoom(0.9));
  document.getElementById('reset-view')?.addEventListener('click', resetView);
  document.getElementById('toggle-categories')?.addEventListener('click', toggleCategories);

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
        highlightCategory(node);
        draw();
      }
    }
  }

  function handleMouseUp() {
    isDragging = false;
    canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  }

  function highlightCategory(node) {
    if (!categoriesEl) return;
    
    // Clear all highlights
    const categoryItems = categoriesEl.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
      item.classList.remove('highlighted');
    });
    
    // Highlight the category for the hovered node
    if (node && categoryMap[node.category]) {
      const categoryName = categoryMap[node.category];
      const categoryItem = Array.from(categoryItems).find(item => 
        item.querySelector('.category-label').textContent === categoryName
      );
      if (categoryItem) {
        categoryItem.classList.add('highlighted');
      }
    }
  }

  function handleWheel(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Much slower zoom - smaller increments
    const zoomFactor = e.deltaY > 0 ? 0.95 : 1.05;
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
        // Convert newlines to HTML line breaks for proper bullet point display
        detailsDesc.innerHTML = selectedNode.description.replace(/\n/g, '<br>');
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
    scale = 0.6; // More zoomed out by default
    offsetX = 0;
    offsetY = 0;
    selectedNode = null;
    draw();
  }

  function toggleCategories() {
    if (!categoriesEl) return;
    categoriesEl.classList.toggle('hidden');
    
    // Update button text to show current state
    const toggleBtn = document.getElementById('toggle-categories');
    if (toggleBtn) {
      toggleBtn.textContent = categoriesEl.classList.contains('hidden') ? '📋' : '✕';
      toggleBtn.title = categoriesEl.classList.contains('hidden') ? 'Show Categories' : 'Hide Categories';
    }
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

    // Draw connections with improved logic to avoid duplicates
    ctx.strokeStyle = 'rgba(77, 124, 255, 0.4)';
    ctx.lineWidth = 1.5;
    const drawnConnections = new Set();
    
    for (let node of techNodes) {
      for (let connectionId of node.connections) {
        const targetNode = techNodes.find(n => n.id === connectionId);
        if (targetNode) {
          // Create a unique key for this connection to avoid duplicates
          const connectionKey = [node.id, targetNode.id].sort().join('-');
          if (!drawnConnections.has(connectionKey)) {
            drawnConnections.add(connectionKey);
            drawRectangularConnection(node, targetNode);
          }
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

  // Helper: draw clean straight connections
  function drawRectangularConnection(sourceNode, targetNode) {
    const dx = targetNode.x - sourceNode.x;
    const dy = targetNode.y - sourceNode.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Only draw connections for reasonable distances to avoid clutter
    if (distance > 50) {
      // Draw straight line connection
      ctx.beginPath();
      ctx.moveTo(sourceNode.x, sourceNode.y);
      ctx.lineTo(targetNode.x, targetNode.y);
      ctx.stroke();
      
      // Draw simple arrow at the end
      const angle = Math.atan2(dy, dx);
      const arrowLength = 10;
      const arrowAngle = Math.PI / 6;
      
      ctx.beginPath();
      ctx.moveTo(targetNode.x, targetNode.y);
      ctx.lineTo(
        targetNode.x - arrowLength * Math.cos(angle - arrowAngle),
        targetNode.y - arrowLength * Math.sin(angle - arrowAngle)
      );
      ctx.moveTo(targetNode.x, targetNode.y);
      ctx.lineTo(
        targetNode.x - arrowLength * Math.cos(angle + arrowAngle),
        targetNode.y - arrowLength * Math.sin(angle + arrowAngle)
      );
      ctx.stroke();
    }
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



// Update this during EC2/deploy step to your backend URL
let API = "http://localhost:5005";

async function upload() {
  const album = document.getElementById('album').value || 'default';
  const fileEl = document.getElementById('image');
  if (!fileEl.files.length) { alert("Select a file"); return; }
  const file = fileEl.files[0];

  const fd = new FormData();
  fd.append('album', album);
  fd.append('image', file);

  const res = await fetch(API + '/upload', { method: 'POST', body: fd });
  const out = document.getElementById('output');
  try {
    const data = await res.json();
    if (res.ok) {
      // show a short success message and a small thumbnail/link
      out.innerHTML = '';
      const p = document.createElement('p');
      p.textContent = 'Successfully uploaded.';
      p.style.color = 'green';
      out.appendChild(p);
      if (data.url) {
        const a = document.createElement('a');
        a.href = data.url;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = 'View image';
        out.appendChild(a);

        const img = document.createElement('img');
        img.src = data.url;
        img.width = 150;
        img.style.display = 'block';
        img.style.marginTop = '8px';
        // If presigned/private, the URL will work; otherwise it may 403 until public
        img.onerror = () => { img.style.display = 'none'; };
        out.appendChild(img);
      }
    } else {
      out.innerHTML = '';
      const p = document.createElement('p');
      p.textContent = 'Upload failed: ' + (data.error || JSON.stringify(data));
      p.style.color = 'red';
      out.appendChild(p);
    }
  } catch (err) {
    alert('Unexpected response: ' + err);
  }
}

async function fetchAlbums() {
  try {
    const res = await fetch(API + '/albums');
    if (!res.ok) {
      const text = await res.text();
      throw new Error('Failed to fetch albums: ' + res.status + ' ' + text);
    }
    const data = await res.json();
    const out = document.getElementById('output');
    out.innerHTML = '';
    if (!data || Object.keys(data).length === 0) {
      const p = document.createElement('p');
      p.textContent = 'No albums found. Try uploading some images first.';
      out.appendChild(p);
      return;
    }

    for (const [album, imgs] of Object.entries(data)) {
      const albumDiv = document.createElement('div');
      albumDiv.className = 'album';
      
      const h = document.createElement('h3');
      h.textContent = album;
      albumDiv.appendChild(h);

      const grid = document.createElement('div');
      grid.className = 'image-grid';
      
      imgs.forEach(item => {
        const imgContainer = document.createElement('div');
        imgContainer.className = 'image-container';
        
        const img = document.createElement('img');
        // item may be a string (legacy) or an object {key, url}
        if (typeof item === 'string') {
          img.src = item;
        } else if (item && item.key) {
          // use backend proxy to avoid CORS / private object issues
          img.src = API + '/image/' + encodeURIComponent(item.key);
        } else if (item && item.url) {
          img.src = item.url;
        }
        
        // show an inline placeholder if image fails to load
        img.onerror = () => { imgContainer.style.display = 'none'; };
        
        // Click to open in new tab for full resolution
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
          window.open(img.src, '_blank');
        });
        
        imgContainer.appendChild(img);
        grid.appendChild(imgContainer);
      });
      
      albumDiv.appendChild(grid);
      out.appendChild(albumDiv);
    }
  } catch (err) {
    console.error(err);
    alert('Error fetching albums: ' + err.message);
  }
}

// Modal helpers
function openImageModal(src) {
  const modal = document.getElementById('image-modal');
  const modalImg = document.getElementById('modal-img');
  const close = document.getElementById('modal-close');
  modalImg.src = src;
  modal.style.display = 'flex';
  // close handlers
  close.onclick = () => { modal.style.display = 'none'; modalImg.src = ''; };
  modal.onclick = (e) => { if (e.target === modal) { modal.style.display = 'none'; modalImg.src = ''; } };
  document.onkeydown = (e) => { if (e.key === 'Escape') { modal.style.display = 'none'; modalImg.src = ''; document.onkeydown = null; } };
}

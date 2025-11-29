let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let img = new Image();
let trulyOriginalImageData = null;

// New cropping variables
//let isCropping = false;
//let cropStartX = 0;
//let cropStartY = 0;
//let cropEndX = 0;
//let cropEndY = 0;

// Fit canvas to image
function fitCanvasToImage(w, h) {
  canvas.width = w;
  canvas.height = h;
}

// Load image from file
document.getElementById('fileInput').addEventListener('change', function(e){
  const f = e.target.files[0];
  if(!f) return;
  const reader = new FileReader();
  reader.onload = function(ev){
    loadImage(ev.target.result);
  }
  reader.readAsDataURL(f);
});

// Load image from base64 or URL
function loadImage(src) {
  img.onload = function() {
    fitCanvasToImage(img.width, img.height);
    ctx.drawImage(img, 0, 0);
    trulyOriginalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    document.getElementById('resultImg').src = canvas.toDataURL();
  };
  img.src = src;
}

// Apply preset directly like grayscale
function applyPreset(preset){
  if(!trulyOriginalImageData) return;

  let data = new ImageData(
    new Uint8ClampedArray(trulyOriginalImageData.data),
    trulyOriginalImageData.width,
    trulyOriginalImageData.height
  );

  if(preset === 'sepia') data = applySepia(data);
  if(preset === 'fade') data = applyFade(data);
  if(preset === 'grey') data = applyGrey(data);

  ctx.putImageData(data, 0, 0);
  document.getElementById('resultImg').src = canvas.toDataURL();
}

// Preset functions
function applySepia(data){
  for(let i=0;i<data.data.length;i+=4){
    let r = data.data[i], g = data.data[i+1], b = data.data[i+2];
    data.data[i] = Math.min(255, 0.393*r + 0.769*g + 0.189*b);
    data.data[i+1] = Math.min(255, 0.349*r + 0.686*g + 0.168*b);
    data.data[i+2] = Math.min(255, 0.272*r + 0.534*g + 0.131*b);
  }
  return data;
}

function applyFade(data){
  for(let i=0;i<data.data.length;i+=4){
    data.data[i] = Math.min(255, data.data[i]*0.8 + 40);
    data.data[i+1] = Math.min(255, data.data[i+1]*0.8 + 40);
    data.data[i+2] = Math.min(255, data.data[i+2]*0.8 + 40);
  }
  return data;
}

function applyGrey(data){
  for(let i=0;i<data.data.length;i+=4){
    let v = 0.2126*data.data[i] + 0.7152*data.data[i+1] + 0.0722*data.data[i+2];
    data.data[i] = data.data[i+1] = data.data[i+2] = v;
  }
  return data;
}

// Slider events (brightness & contrast still work on original image)
function applyBrightnessContrast(){
  if(!trulyOriginalImageData) return;

  let data = new ImageData(
    new Uint8ClampedArray(trulyOriginalImageData.data),
    trulyOriginalImageData.width,
    trulyOriginalImageData.height
  );

  let b = parseInt(document.getElementById('brightness').value, 10);
  let c = parseInt(document.getElementById('contrast').value, 10);
  const factor = (259 * (c + 255)) / (255 * (259 - c));

  for(let i=0;i<data.data.length;i+=4){
    for(let ch=0; ch<3; ch++){
      let val = data.data[i+ch];
      val = factor*(val-128)+128 + b;
      data.data[i+ch] = Math.max(0,Math.min(255,val));
    }
  }

  ctx.putImageData(data, 0, 0);
  document.getElementById('resultImg').src = canvas.toDataURL();
}

// Sliders
document.getElementById('brightness').addEventListener('input', applyBrightnessContrast);
document.getElementById('contrast').addEventListener('input', applyBrightnessContrast);

// Presets buttons
document.getElementById('sepia').addEventListener('click', ()=>applyPreset('sepia'));
document.getElementById('fade').addEventListener('click', ()=>applyPreset('fade'));
document.getElementById('grey2').addEventListener('click', ()=>applyPreset('grey'));

// Grayscale button (same as other presets)
document.getElementById('grayscale').addEventListener('click', ()=>applyPreset('grey'));




// Reset
document.getElementById('reset').addEventListener('click', ()=>{
  if(!trulyOriginalImageData) return;
  // This creates a fresh ImageData object from the original data (since trulyOriginalImageData might be cropped)
  const resetData = new ImageData(
    new Uint8ClampedArray(trulyOriginalImageData.data),
    trulyOriginalImageData.width,
    trulyOriginalImageData.height
  );
  fitCanvasToImage(resetData.width, resetData.height);
  ctx.putImageData(resetData, 0, 0);
  document.getElementById('brightness').value = 0;
  document.getElementById('contrast').value = 0;
  document.getElementById('resultImg').src = canvas.toDataURL();
});

document.querySelectorAll(".server").forEach(btn => {
  btn.addEventListener("click", async (ev) => {
    ev.preventDefault();
    const filter = btn.dataset.filter;
    console.log("[client] server button clicked:", filter);

    // ensure an image is present on canvas
    if (!canvas.width || !canvas.height) {
      console.error("[client] canvas empty - load an image first");
      return;
    }

    const imgB64 = canvas.toDataURL("image/png");
    console.log("[client] sending image b64 length:", imgB64.length);

    try {
      const res = await fetch("process_image/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filter: filter, image_b64: imgB64 })
      });

      console.log("[client] fetch returned, status:", res.status);
      const data = await res.json();
      console.log("[client] response JSON:", data);

      if (data.status === "ok") {
        document.getElementById("resultImg").src = data.image_b64;
      } else {
        alert("Server filter failed: " + (data.msg || JSON.stringify(data)));
      }
    } catch (err) {
      console.error("[client] fetch error:", err);
      alert("Network/error talking to server. See console.");
    }
  });
});

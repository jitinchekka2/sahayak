import { streamGemini } from './gemini-api.js';

let form = document.querySelector('form');
let promptInput = document.querySelector('input[name="prompt"]');
let output = document.querySelector('.output');
let fileUploadSection = document.querySelector('.file-upload');
let imageUpload = document.querySelector('#image-upload');
let uploadChoice = document.querySelector('input[value="uploaded"]');
let uploadedPreview = document.querySelector('.uploaded-preview');
let uploadPlaceholder = document.querySelector('.upload-placeholder');

// Store uploaded image data
let uploadedImageData = null;

// Handle radio button changes to show/hide file upload section
form.addEventListener('change', (ev) => {
  if (ev.target.name === 'chosen-image') {
    if (ev.target.value === 'uploaded') {
      fileUploadSection.style.display = 'block';
      // Clear any previous messages when switching to upload mode
      output.textContent = '';
    } else {
      fileUploadSection.style.display = 'none';
      output.textContent = '';
    }
  }
});

// Handle file upload
imageUpload.addEventListener('change', (ev) => {
  const file = ev.target.files[0];
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      // Store the base64 data (remove the data:image/...;base64, prefix)
      uploadedImageData = {
        base64: e.target.result.split(',')[1],
        mimeType: file.type
      };

      // Show preview
      uploadedPreview.src = e.target.result;
      uploadedPreview.style.display = 'block';
      uploadPlaceholder.style.display = 'none';

      // Automatically select the upload option
      uploadChoice.checked = true;
    };
    reader.readAsDataURL(file);
  }
});

form.onsubmit = async (ev) => {
  ev.preventDefault();
  output.textContent = 'Generating...';

  try {
    let imageBase64;
    let mimeType = 'image/jpeg';
    let selectedImageValue = form.elements.namedItem('chosen-image')?.value;
    let hasImage = false;

    if (selectedImageValue === 'uploaded') {
      // Use uploaded image
      if (!uploadedImageData) {
        output.textContent = 'Please upload an image first.';
        return;
      }
      imageBase64 = uploadedImageData.base64;
      mimeType = uploadedImageData.mimeType;
      hasImage = true;
    } else if (selectedImageValue && selectedImageValue !== 'none') {
      // Use predefined image with caching
      let imageUrl = selectedImageValue;
      if (!window._imageBase64Cache) window._imageBase64Cache = {};
      if (window._imageBase64Cache[imageUrl]) {
        imageBase64 = window._imageBase64Cache[imageUrl];
      } else {
        imageBase64 = await fetch(imageUrl)
          .then(r => r.arrayBuffer())
          .then(a => base64js.fromByteArray(new Uint8Array(a)));
        window._imageBase64Cache[imageUrl] = imageBase64;
      }
      hasImage = true;
    }

    // Assemble the prompt - include image only if one is selected
    let parts = [{ text: promptInput.value }];
    if (hasImage) {
      parts.unshift({ inline_data: { mime_type: mimeType, data: imageBase64, } });
    }

    let contents = [
      {
        role: 'user',
        parts: parts
      }
    ];

    // Call the multimodal model, and get a stream of results
    let stream = streamGemini({
      model: 'gemini-2.0-flash',
      contents,
    });

    // Read from the stream and interpret the output as markdown
    let buffer = [];
    let md = new markdownit();
    for await (let chunk of stream) {
      buffer.push(chunk);
      output.innerHTML = md.render(buffer.join(''));
    }
  } catch (e) {
    output.textContent += '\n---\n' + e;
  }
};
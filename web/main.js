import { streamGemini } from './gemini-api.js';

let form = document.querySelector('form');
let promptInput = document.querySelector('input[name="prompt"]');
let output = document.querySelector('.output');

form.onsubmit = async (ev) => {
  ev.preventDefault();
  output.textContent = 'Generating...';

  try {
    // Load the image as a base64 string with caching
    let imageUrl = form.elements.namedItem('chosen-image').value;
    if (!window._imageBase64Cache) window._imageBase64Cache = {};
    let imageBase64;
    if (window._imageBase64Cache[imageUrl]) {
      imageBase64 = window._imageBase64Cache[imageUrl];
    } else {
      imageBase64 = await fetch(imageUrl)
        .then(r => r.arrayBuffer())
        .then(a => base64js.fromByteArray(new Uint8Array(a)));
      window._imageBase64Cache[imageUrl] = imageBase64;
    }

    // Assemble the prompt by combining the text with the chosen image
    let contents = [
      {
        role: 'user',
        parts: [
          { inline_data: { mime_type: 'image/jpeg', data: imageBase64, } },
          { text: promptInput.value }
        ]
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
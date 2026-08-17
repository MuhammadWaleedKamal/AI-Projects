async function generateAIResponse() {
  const input = document.getElementById('userInput').value;
  const task = document.getElementById('taskSelect').value; // Dropdown value
  const fileInput = document.getElementById('fileInput');
  const loader = document.getElementById('loader');
  const resultContainer = document.getElementById('resultContainer');
  const resultText = document.getElementById('resultText');
  const submitBtn = document.getElementById('submitBtn');

  const selectedFile = fileInput.files[0];

  if (!input.trim() && !selectedFile) {
    alert('Please enter text OR select a file to process.');
    return;
  }

  loader.classList.remove('hidden');
  resultContainer.classList.add('hidden');
  submitBtn.disabled = true;

  try {
    let response;

    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('task', task); // Sends selected mode

      response = await fetch("/api/analyze_file", {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch("/api/analyze", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input, task: task }) // Sends selected mode
      });
    }

    const data = await response.json();

    if (response.ok) {
      if (window.marked) {
        resultText.innerHTML = marked.parse(data.result);
      } else {
        resultText.innerText = data.result;
      }
      resultContainer.classList.remove('hidden');
    } else {
      alert(data.error || 'Something went wrong.');
    }
  } catch (error) {
    alert('Failed to connect to backend server.');
    console.error(error);
  } finally {
    loader.classList.add('hidden');
    submitBtn.disabled = false;
  }
}

async function handleContactSubmit(event) {
  event.preventDefault();

  const name = document.getElementById('contactName').value;
  const email = document.getElementById('contactEmail').value;
  const message = document.getElementById('contactMessage').value;

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, email, message })
    });

    const data = await response.json();

    if (response.ok) {
      alert(`Thank you, ${name}! Your message has been sent to my inbox.`);
      event.target.reset();
    } else {
      alert(data.error || 'Failed to send message.');
    }
  } catch (error) {
    alert('Server connection error. Make sure backend is running!');
    console.error(error);
  }
}

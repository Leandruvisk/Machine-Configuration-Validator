const form = document.getElementById('device-form');
const table = document.getElementById('device-table');

async function fetchDevices() {
  const response = await fetch('/api/devices');
  const devices = await response.json();
  table.innerHTML = devices.map(device => `
    <tr>
      <td>${device.id}</td>
      <td>${device.name}</td>
      <td>${device.device_type}</td>
      <td>${device.serial_number}</td>
      <td>${device.location}</td>
    </tr>
  `).join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    name: formData.get('name'),
    device_type: formData.get('device_type'),
    serial_number: formData.get('serial_number'),
    location: formData.get('location'),
  };

  const response = await fetch('/api/devices', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (response.ok) {
    form.reset();
    await fetchDevices();
  } else {
    const error = await response.json();
    alert(error.detail || 'Erro ao cadastrar dispositivo');
  }
});

async function fetchMqttStatus() {
  const statusContainer = document.getElementById('mqtt-status');
  try {
    const response = await fetch('/api/mqtt/latest');
    const data = await response.json();
    if (!Object.keys(data).length) {
      statusContainer.innerHTML = '<p>Nenhuma mensagem MQTT recebida ainda.</p>';
      return;
    }

    statusContainer.innerHTML = Object.entries(data).map(([topic, item]) => `
      <div class="mqtt-item">
        <strong>Tópico:</strong> ${topic}<br />
        <strong>Timestamp:</strong> ${item.timestamp || 'sem timestamp'}<br />
        <strong>Payload:</strong> <pre>${JSON.stringify(item.payload, null, 2)}</pre>
      </div>
    `).join('');
  } catch (error) {
    statusContainer.innerHTML = `<p>Erro ao consultar MQTT: ${error.message}</p>`;
  }
}

fetchDevices();
fetchMqttStatus();
setInterval(fetchMqttStatus, 10000);

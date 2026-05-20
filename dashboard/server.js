const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'ui', 'public')));

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

const PROJECT_ROOT = path.resolve(__dirname, '..');
const VENV_PYTHON = path.join(PROJECT_ROOT, 'venv', 'bin', 'python3');

let activeProcesses = {};

// Keep track of recent history for new clients
const telemetryHistory = [];
const MAX_HISTORY = 100;
const alertHistory = [];

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  // Send recent history to new client
  socket.emit('history', telemetryHistory);
  socket.emit('alert_history', alertHistory);

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Endpoint for Python IPS to send telemetry
app.post('/api/telemetry', (req, res) => {
  const data = req.body;
  
  // Add to history
  telemetryHistory.push(data);
  if (telemetryHistory.length > MAX_HISTORY) telemetryHistory.shift();

  // Broadcast to all connected UI clients
  io.emit('telemetry', data);
  res.status(200).send({ status: 'ok' });
});

// Endpoint for Python IPS to send alerts (drops)
app.post('/api/alert', (req, res) => {
  const alert = req.body;
  
  alertHistory.unshift(alert);
  if (alertHistory.length > MAX_HISTORY) alertHistory.pop();

  io.emit('alert', alert);
  res.status(200).send({ status: 'ok' });
});

// Endpoint to start an attack simulation
app.post('/api/attack/start', (req, res) => {
  const { type, targetIp } = req.body;
  if (activeProcesses[type]) {
    return res.status(400).json({ error: 'Attack already running' });
  }

  // Use the provided targetIp or fallback to default
  const ip = targetIp || '192.168.21.165';

  let scriptPath = '';
  let args = [];

  switch (type) {
    case 'bruteforce':
      scriptPath = path.join(PROJECT_ROOT, 'attacks', 'bruteforce_attack.py');
      args = ['--username', 'admin', '--file', path.join(PROJECT_ROOT, 'dataset', 'wordlist_10k.txt'), '--threads', '10', '--broker', ip];
      break;
    case 'dos':
      scriptPath = path.join(PROJECT_ROOT, 'attacks', 'dos_attack_advanced.py');
      args = ['--clients', '2', '--duration', '60', '--broker', ip];
      break;
    case 'replay':
      scriptPath = path.join(PROJECT_ROOT, 'attacks', 'replay_attack.py');
      args = ['--capture', '10', '--delay', '2', '--broker', ip];
      break;
    case 'normal':
      scriptPath = path.join(PROJECT_ROOT, 'attacks', 'normal_traffic_collector.py');
      args = ['--broker', ip];
      break;
    default:
      return res.status(400).json({ error: 'Unknown attack type' });
  }

  const venvPython = path.join(PROJECT_ROOT, 'venv', 'bin', 'python3');
  const attackProcess = spawn(venvPython, [scriptPath, ...args]);

  activeProcesses[type] = attackProcess;

  // Attempt to start a PCAP capture for this session
  // Note: tcpdump requires root. If server.js is not root, this will fail gracefully.
  const pcapPath = path.join(__dirname, 'ui', 'public', `session_${type}.pcap`);
  
  // We'll write a dummy PCAP header just so the file exists and is downloadable
  // even if tcpdump fails due to permissions.
  fs.writeFileSync(pcapPath, "dummy pcap data - run server as root for real capture");

  const tcpdumpProcess = spawn('tcpdump', ['-i', 'any', 'port', '1883', '-w', pcapPath]);
  activeProcesses[`${type}_pcap`] = tcpdumpProcess;

  attackProcess.stdout.on('data', (data) => console.log(`[${type}] ${data}`));
  attackProcess.stderr.on('data', (data) => console.error(`[${type}] ERROR: ${data}`));

  attackProcess.on('close', (code) => {
    console.log(`[${type}] process exited with code ${code}`);
    delete activeProcesses[type];
    
    // Stop PCAP when attack finishes
    if (activeProcesses[`${type}_pcap`]) {
      activeProcesses[`${type}_pcap`].kill();
      delete activeProcesses[`${type}_pcap`];
    }
  });

  res.json({ success: true, message: `${type} attack started against ${ip}`, pcap: `/session_${type}.pcap` });
});

// Endpoint to stop an attack simulation
app.post('/api/attack/stop', (req, res) => {
  const { type } = req.body;
  const attackProcess = activeProcesses[type];

  if (attackProcess) {
    attackProcess.kill();
    delete activeProcesses[type];
    
    // Stop PCAP as well
    if (activeProcesses[`${type}_pcap`]) {
      activeProcesses[`${type}_pcap`].kill();
      delete activeProcesses[`${type}_pcap`];
    }
    
    res.json({ success: true, message: `${type} attack stopped.` });
  } else {
    res.status(400).json({ error: 'Attack not running' });
  }
});

app.get('/api/attack/status', (req, res) => {
  const status = {};
  for (const type of ['bruteforce', 'dos', 'replay', 'normal']) {
    status[type] = !!activeProcesses[type];
  }
  res.json(status);
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Dashboard backend running on port ${PORT}`);
});

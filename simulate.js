#!/usr/bin/env node
// simulate.js — Dev tool for triggering drift/refocus signals in running Glorb app.
// Usage: node simulate.js drift
//        node simulate.js refocus

const net = require('net')

const SOCK_PATH = '/tmp/glorb-ipc.sock'
const cmd = process.argv[2]

if (!cmd || !['drift', 'refocus'].includes(cmd)) {
  console.error('Usage: node simulate.js <drift|refocus>')
  process.exit(1)
}

const socket = net.createConnection(SOCK_PATH, () => {
  socket.write(cmd + '\n')
})

let response = ''

socket.on('data', (chunk) => {
  response += chunk.toString()
})

socket.on('end', () => {
  const trimmed = response.trim()
  if (trimmed === 'ok') {
    console.log(`[simulate] ${cmd} signal sent successfully.`)
    process.exit(0)
  } else {
    console.error(`[simulate] Unexpected response: ${trimmed}`)
    process.exit(1)
  }
})

socket.on('error', (err) => {
  if (err.code === 'ENOENT' || err.code === 'ECONNREFUSED') {
    console.error('[simulate] Could not connect — is Glorb running?')
  } else {
    console.error('[simulate] Connection error:', err.message)
  }
  process.exit(1)
})

// Timeout: if no response in 3s, give up
setTimeout(() => {
  console.error('[simulate] Timed out — no response from Glorb.')
  socket.destroy()
  process.exit(1)
}, 3000)

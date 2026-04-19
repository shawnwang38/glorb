#!/usr/bin/env node
/*
 * setup-python.cjs — bootstrap camera_detect/.venv with detection deps.
 *
 * Run automatically by `npm install` (via postinstall in package.json).
 * Idempotent: safe to re-run; skips work when the venv is already healthy.
 * Graceful: if no compatible Python is present, warns and exits 0 so that
 *           `npm install` still succeeds. The Electron app falls back to
 *           running without camera detection in that case.
 */

const { spawnSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const VENV_DIR = path.join(ROOT, 'camera_detect', '.venv')
const VENV_PY = path.join(VENV_DIR, 'bin', 'python')
const VENV_PIP = path.join(VENV_DIR, 'bin', 'pip')
const REQS = path.join(ROOT, 'camera_detect', 'requirements.txt')

// mediapipe 0.10 publishes wheels for CPython 3.9–3.13. 3.14 is not yet supported.
const MIN_MAJOR = 3
const MIN_MINOR = 9
const MAX_MINOR = 13

const CANDIDATES = [
  'python3.13', 'python3.12', 'python3.11', 'python3.10', 'python3.9',
  '/opt/homebrew/bin/python3.13',
  '/opt/homebrew/bin/python3.12',
  '/opt/homebrew/bin/python3.11',
  '/opt/homebrew/bin/python3.10',
  'python3',
]

function log (msg) { console.log(`[setup-python] ${msg}`) }
function warn (msg) { console.warn(`[setup-python] ${msg}`) }

function parsePythonVersion (bin) {
  const r = spawnSync(bin, ['-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'], {
    encoding: 'utf8',
  })
  if (r.status !== 0 || !r.stdout) return null
  const m = r.stdout.trim().match(/^(\d+)\.(\d+)$/)
  if (!m) return null
  return { major: parseInt(m[1], 10), minor: parseInt(m[2], 10) }
}

function isCompatible (v) {
  if (!v) return false
  if (v.major !== MIN_MAJOR) return false
  return v.minor >= MIN_MINOR && v.minor <= MAX_MINOR
}

function findCompatiblePython () {
  const seen = new Set()
  for (const cand of CANDIDATES) {
    if (seen.has(cand)) continue
    seen.add(cand)
    const v = parsePythonVersion(cand)
    if (isCompatible(v)) return { bin: cand, version: `${v.major}.${v.minor}` }
  }
  return null
}

function venvLooksHealthy () {
  // .venv/bin/python is a symlink to the host interpreter — if the host
  // version was uninstalled, the symlink dangles and the venv is unusable.
  try {
    const r = spawnSync(VENV_PY, ['-c', 'import sys; print(sys.version_info.major, sys.version_info.minor)'], { encoding: 'utf8' })
    return r.status === 0
  } catch {
    return false
  }
}

function depsInstalled () {
  const r = spawnSync(VENV_PY, ['-c', 'import cv2, mediapipe, numpy'], { encoding: 'utf8' })
  return r.status === 0
}

function run (bin, args, opts = {}) {
  const r = spawnSync(bin, args, { stdio: 'inherit', ...opts })
  if (r.status !== 0) {
    throw new Error(`command failed (exit ${r.status}): ${bin} ${args.join(' ')}`)
  }
}

function main () {
  if (!fs.existsSync(REQS)) {
    warn(`requirements.txt not found at ${REQS}; skipping`)
    return 0
  }

  // Fast path: existing venv works and has deps → nothing to do.
  if (venvLooksHealthy() && depsInstalled()) {
    log('venv already set up with detection deps (ok)')
    return 0
  }

  // Rebuild if broken.
  if (fs.existsSync(VENV_DIR) && !venvLooksHealthy()) {
    log('existing venv is broken (dangling symlink); rebuilding')
    fs.rmSync(VENV_DIR, { recursive: true, force: true })
  }

  // Need to (re)create the venv.
  if (!fs.existsSync(VENV_DIR)) {
    const py = findCompatiblePython()
    if (!py) {
      warn(`no compatible Python found (need CPython 3.${MIN_MINOR}–3.${MAX_MINOR}).`)
      warn('camera detection will be disabled. Install python@3.11 via homebrew and re-run:')
      warn('  brew install python@3.11 && npm run setup:python')
      return 0 // non-fatal — don't break npm install
    }
    log(`creating venv at ${VENV_DIR} using ${py.bin} (Python ${py.version})`)
    try {
      run(py.bin, ['-m', 'venv', VENV_DIR])
    } catch (err) {
      warn(`venv creation failed: ${err.message}`)
      warn('camera detection will be disabled.')
      return 0
    }
  }

  // Install deps (idempotent; pip is a fast no-op when already up to date).
  log('upgrading pip')
  try { run(VENV_PY, ['-m', 'pip', 'install', '--upgrade', 'pip', '--quiet']) } catch { /* non-fatal */ }

  log(`installing detection deps from ${path.relative(ROOT, REQS)}`)
  try {
    run(VENV_PIP, ['install', '-r', REQS])
  } catch (err) {
    warn(`pip install failed: ${err.message}`)
    warn('camera detection will be disabled until deps are installed.')
    return 0
  }

  if (!depsInstalled()) {
    warn('deps installed but import check failed; camera detection may not work.')
    return 0
  }

  log('camera detection ready')
  return 0
}

process.exit(main())

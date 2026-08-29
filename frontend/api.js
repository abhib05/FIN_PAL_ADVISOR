/* =========================================================
   FinPal — API layer + shared helpers
   Framework-free. Loaded with <script src="api.js"></script>.

   Backend contract (FastAPI, app/api/voice.py):
     POST /api/sessions                        -> { session_id, user_id }
     POST /api/sessions/{id}/chat/stream       <- { message }  -> SSE token/done/error
     POST /api/sessions/{id}/voice             <- multipart field "audio"
                                               -> { user_text, advisor_text, audio_b64, profile }
     GET  /api/sessions/{id}/profile           -> profile object

   API base resolution, first match wins:
     1. window.FINPAL_API_BASE set before this script loads
     2. ?api=<base> in the query string (dev convenience)
     3. file:// pages -> http://localhost:8000
     4. same origin ('')  <- production default
   ========================================================= */
(function (global) {
  'use strict';

  var DEV_FALLBACK = 'http://localhost:8000';

  function resolveBase() {
    if (typeof global.FINPAL_API_BASE === 'string') {
      return global.FINPAL_API_BASE.replace(/\/+$/, '');
    }
    try {
      var override = new URLSearchParams(global.location.search).get('api');
      if (override) return override.replace(/\/+$/, '');
    } catch (e) { /* ignore malformed query strings */ }

    if (global.location && global.location.protocol === 'file:') return DEV_FALLBACK;
    return ''; // same origin
  }

  var BASE = resolveBase();

  function url(path) { return BASE + path; }

  /* ---------------------------------------------------------
     Errors
     --------------------------------------------------------- */
  function ApiError(message, status) {
    var err = new Error(message);
    err.name = 'ApiError';
    err.status = status || 0;
    return err;
  }

  function friendly(status, fallback) {
    if (status === 404) return 'That session no longer exists. Start a new conversation.';
    if (status === 422) return 'Could not understand that audio — please try again.';
    if (status === 429) return 'The advisor is busy right now. Wait a moment and try again.';
    if (status >= 500)  return 'The advisor service is having trouble. Try again shortly.';
    return fallback || 'Something went wrong. Please try again.';
  }

  /* The backend's own detail text is usually the friendliest thing to show,
     except for 404 where "Session not found" needs the user-facing wording. */
  function messageFor(status, detail, fallback) {
    if (status === 404) return friendly(404);
    return detail || friendly(status, fallback);
  }

  function readDetail(res) {
    return res.text().then(function (body) {
      try {
        var parsed = JSON.parse(body);
        if (parsed && typeof parsed.detail === 'string') return parsed.detail;
      } catch (e) { /* not JSON — fall through */ }
      return '';
    }).catch(function () { return ''; });
  }

  /* ---------------------------------------------------------
     Endpoints
     --------------------------------------------------------- */
  function createSession() {
    return fetch(url('/api/sessions'), { method: 'POST' })
      .catch(function () { throw ApiError('Cannot reach the FinPal API. Is the backend running?', 0); })
      .then(function (res) {
        if (!res.ok) {
          return readDetail(res).then(function (d) {
            throw ApiError(messageFor(res.status, d, 'Could not start a session.'), res.status);
          });
        }
        return res.json();
      });
  }

  function getProfile(sessionId) {
    return fetch(url('/api/sessions/' + encodeURIComponent(sessionId) + '/profile'))
      .catch(function () { throw ApiError('Cannot reach the FinPal API. Is the backend running?', 0); })
      .then(function (res) {
        if (!res.ok) {
          return readDetail(res).then(function (d) {
            throw ApiError(messageFor(res.status, d, 'Could not load your profile.'), res.status);
          });
        }
        return res.json();
      });
  }

  /**
   * Stream a text turn. Handlers: onToken(text), onDone({profile,user_text}),
   * onError(Error). Resolves once the stream is fully consumed.
   * Malformed SSE lines are skipped rather than throwing.
   */
  function streamChat(sessionId, message, handlers) {
    handlers = handlers || {};
    var onToken = handlers.onToken || function () {};
    var onDone  = handlers.onDone  || function () {};
    var onError = handlers.onError || function () {};

    function dispatch(payload) {
      if (!payload || typeof payload !== 'object') return;
      if (payload.type === 'token' && typeof payload.text === 'string') onToken(payload.text);
      else if (payload.type === 'done') onDone(payload);
      else if (payload.type === 'error') onError(ApiError(payload.text || friendly(0), 0));
    }

    function consumeBlock(block) {
      // An SSE block may hold several "data:" lines; the server sends one.
      block.split('\n').forEach(function (line) {
        var trimmed = line.trim();
        if (trimmed.indexOf('data:') !== 0) return;
        var raw = trimmed.slice(5).trim();
        if (!raw || raw === '[DONE]') return;
        try { dispatch(JSON.parse(raw)); }
        catch (e) { /* malformed event — ignore and keep streaming */ }
      });
    }

    return fetch(url('/api/sessions/' + encodeURIComponent(sessionId) + '/chat/stream'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
      body: JSON.stringify({ message: message })
    })
      .catch(function () { throw ApiError('Cannot reach the FinPal API. Is the backend running?', 0); })
      .then(function (res) {
        if (!res.ok) {
          return readDetail(res).then(function (d) {
            throw ApiError(messageFor(res.status, d, 'The advisor could not reply.'), res.status);
          });
        }

        // Browsers without streaming bodies: take the whole payload at once.
        if (!res.body || typeof res.body.getReader !== 'function') {
          return res.text().then(function (text) {
            text.split('\n\n').forEach(consumeBlock);
          });
        }

        var reader  = res.body.getReader();
        var decoder = new TextDecoder();
        var buffer  = '';

        function pump() {
          return reader.read().then(function (chunk) {
            if (chunk.done) {
              if (buffer.trim()) consumeBlock(buffer);
              return;
            }
            buffer += decoder.decode(chunk.value, { stream: true });
            var blocks = buffer.split('\n\n');
            buffer = blocks.pop();               // keep the trailing partial block
            blocks.forEach(consumeBlock);
            return pump();
          });
        }
        return pump();
      });
  }

  function sendVoice(sessionId, blob, filename) {
    var fd = new FormData();
    fd.append('audio', blob, filename || 'recording.webm');

    return fetch(url('/api/sessions/' + encodeURIComponent(sessionId) + '/voice'), {
      method: 'POST',
      body: fd
    })
      .catch(function () { throw ApiError('Cannot reach the FinPal API. Is the backend running?', 0); })
      .then(function (res) {
        if (!res.ok) {
          return readDetail(res).then(function (d) {
            throw ApiError(messageFor(res.status, d, 'Could not process that recording.'), res.status);
          });
        }
        return res.json();
      });
  }

  /* ---------------------------------------------------------
     Microphone
     --------------------------------------------------------- */
  var MIME_CANDIDATES = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/ogg',
    'audio/mp4'
  ];

  function pickMimeType() {
    if (typeof MediaRecorder === 'undefined') return '';
    for (var i = 0; i < MIME_CANDIDATES.length; i++) {
      try {
        if (MediaRecorder.isTypeSupported(MIME_CANDIDATES[i])) return MIME_CANDIDATES[i];
      } catch (e) { /* isTypeSupported may throw on old engines */ }
    }
    return ''; // let the browser choose its own default
  }

  function extForMime(mime) {
    var m = (mime || '').split(';')[0];
    if (m === 'audio/ogg')  return '.ogg';
    if (m === 'audio/mp4')  return '.mp4';
    if (m === 'audio/wav')  return '.wav';
    if (m === 'audio/mpeg') return '.mp3';
    return '.webm';
  }

  function micSupported() {
    return !!(global.navigator && global.navigator.mediaDevices &&
              global.navigator.mediaDevices.getUserMedia &&
              typeof MediaRecorder !== 'undefined');
  }

  /**
   * Resolves with a started recorder handle: { stop() -> Promise<{blob, filename}> }.
   * Rejects with a readable message when permission or hardware is unavailable.
   */
  function startRecording() {
    if (!micSupported()) {
      return Promise.reject(ApiError(
        'Voice input is not available in this browser. Use the text box instead.', 0));
    }
    return global.navigator.mediaDevices.getUserMedia({ audio: true })
      .catch(function (err) {
        var name = err && err.name;
        var msg = name === 'NotAllowedError' || name === 'SecurityError'
          ? 'Microphone access was blocked. Allow it in the browser, or type instead.'
          : name === 'NotFoundError'
            ? 'No microphone found. Type your message instead.'
            : 'Could not open the microphone. Type your message instead.';
        throw ApiError(msg, 0);
      })
      .then(function (stream) {
        var mime = pickMimeType();
        var recorder;
        try {
          recorder = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
        } catch (e) {
          stream.getTracks().forEach(function (t) { t.stop(); });
          throw ApiError('This browser cannot record audio. Type your message instead.', 0);
        }

        var chunks = [];
        recorder.addEventListener('dataavailable', function (ev) {
          if (ev.data && ev.data.size > 0) chunks.push(ev.data);
        });
        recorder.start();

        return {
          mimeType: recorder.mimeType || mime,
          stop: function () {
            return new Promise(function (resolve) {
              recorder.addEventListener('stop', function () {
                stream.getTracks().forEach(function (t) { t.stop(); });
                var type = recorder.mimeType || mime || 'audio/webm';
                resolve({
                  blob: new Blob(chunks, { type: type }),
                  filename: 'recording' + extForMime(type)
                });
              }, { once: true });
              try { recorder.stop(); }
              catch (e) {
                stream.getTracks().forEach(function (t) { t.stop(); });
                resolve({ blob: new Blob(chunks, { type: 'audio/webm' }), filename: 'recording.webm' });
              }
            });
          }
        };
      });
  }

  /* ---------------------------------------------------------
     Audio playback (base64 WAV from the TTS response)
     --------------------------------------------------------- */
  var currentAudio = null;

  function stopAudio() {
    if (currentAudio) {
      try { currentAudio.pause(); } catch (e) { /* already gone */ }
      currentAudio = null;
    }
  }

  /** Always resolves — playback failure must never break the page. */
  function playBase64Wav(b64) {
    return new Promise(function (resolve) {
      if (!b64) return resolve(false);
      stopAudio();
      var objectUrl;
      try {
        var binary = atob(b64);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        objectUrl = URL.createObjectURL(new Blob([bytes], { type: 'audio/wav' }));
      } catch (e) {
        return resolve(false);
      }

      var audio = new Audio(objectUrl);
      currentAudio = audio;
      var settled = false;
      function finish(ok) {
        if (settled) return;
        settled = true;
        URL.revokeObjectURL(objectUrl);
        if (currentAudio === audio) currentAudio = null;
        resolve(ok);
      }
      audio.addEventListener('ended', function () { finish(true); });
      audio.addEventListener('error', function () { finish(false); });
      var started = audio.play();
      if (started && typeof started.catch === 'function') {
        started.catch(function () { finish(false); });   // autoplay blocked
      }
    });
  }

  /* ---------------------------------------------------------
     Session id in the query string
     --------------------------------------------------------- */
  function sessionFromQuery() {
    try {
      var p = new URLSearchParams(global.location.search);
      return p.get('session') || p.get('sid') || null;
    } catch (e) { return null; }
  }

  function linkWithSession(page, sessionId) {
    return sessionId ? page + '?session=' + encodeURIComponent(sessionId) : page;
  }

  /** Put the session in the address bar without reloading or adding history. */
  function rememberSessionInUrl(sessionId) {
    if (!sessionId || !global.history || !global.history.replaceState) return;
    try {
      var u = new URL(global.location.href);
      u.searchParams.set('session', sessionId);
      global.history.replaceState({}, '', u.toString());
    } catch (e) { /* file:// or old browser — harmless */ }
  }

  /* ---------------------------------------------------------
     Formatting
     --------------------------------------------------------- */
  function inr(value) {
    var n = Number(value);
    if (value === null || value === undefined || value === '' || isNaN(n)) return '—';
    try { return '₹' + Math.round(n).toLocaleString('en-IN'); }
    catch (e) { return '₹' + Math.round(n); }
  }

  function pct(part, whole) {
    var p = Number(part), w = Number(whole);
    if (!w || isNaN(p) || isNaN(w)) return 0;
    return Math.round((p / w) * 100);
  }

  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }

  function titleise(value) {
    if (value === null || value === undefined || value === '') return '—';
    return String(value).replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  global.FinPal = {
    apiBase: BASE,
    createSession: createSession,
    getProfile: getProfile,
    streamChat: streamChat,
    sendVoice: sendVoice,
    startRecording: startRecording,
    micSupported: micSupported,
    pickMimeType: pickMimeType,
    extForMime: extForMime,
    playBase64Wav: playBase64Wav,
    stopAudio: stopAudio,
    sessionFromQuery: sessionFromQuery,
    linkWithSession: linkWithSession,
    rememberSessionInUrl: rememberSessionInUrl,
    inr: inr,
    pct: pct,
    clamp: clamp,
    titleise: titleise
  };
})(window);

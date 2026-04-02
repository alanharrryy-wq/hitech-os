const state = {
  activeView: "health",
  eventsCursor: 0,
  eventsAuto: false,
  eventsTimer: null,
};

const ui = {
  navItems: Array.from(document.querySelectorAll('.nav__item')),
  panels: Array.from(document.querySelectorAll('.panel')),
  pill: document.getElementById('connection-pill'),
  lastSync: document.getElementById('last-sync'),
  refreshAll: document.getElementById('btn-refresh-all'),
  output: {
    health: document.getElementById('health-output'),
    snapshot: document.getElementById('snapshot-output'),
    query: document.getElementById('query-output'),
    command: document.getElementById('command-output'),
    events: document.getElementById('events-output'),
  },
  eventsCursor: document.getElementById('events-cursor'),
  eventsMode: document.getElementById('events-mode'),
};

const api = {
  async request(path, payload) {
    const method = payload ? 'POST' : 'GET';
    const init = {
      method,
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
    };
    if (payload) {
      init.body = JSON.stringify(payload);
    }

    const response = await fetch(`/api/v1${path}`, init);
    const text = await response.text();
    let data = {};
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (error) {
        data = {
          ok: false,
          kind: 'parse_error',
          error: { message: String(error), raw: text.slice(0, 600) },
        };
      }
    }

    if (!response.ok || data.ok === false) {
      const message = data?.error?.message || `HTTP ${response.status}`;
      throw new Error(message);
    }
    return data;
  },

  health() {
    return this.request('/health');
  },

  contracts() {
    return this.request('/contracts');
  },

  snapshot(snapshotId, selector) {
    return this.request('/snapshot', {
      snapshot_id: snapshotId,
      selector,
      context: { client_id: 'web-shell', session_id: 'web-shell-session' },
    });
  },

  query(name, params) {
    return this.request('/query', {
      query: name,
      params,
      context: { client_id: 'web-shell', session_id: 'web-shell-session' },
    });
  },

  command(name, payload, context, idempotencyKey) {
    return this.request('/command', {
      command: name,
      payload,
      context,
      idempotency_key: idempotencyKey,
    });
  },

  events(since) {
    return this.request(`/events?since=${encodeURIComponent(String(since))}&limit=20`);
  },
};

function setConnection(ok, message) {
  ui.pill.classList.remove('pill--ok', 'pill--err', 'pill--pending');
  if (ok === true) {
    ui.pill.classList.add('pill--ok');
    ui.pill.textContent = 'Connected';
  } else if (ok === false) {
    ui.pill.classList.add('pill--err');
    ui.pill.textContent = 'Disconnected';
  } else {
    ui.pill.classList.add('pill--pending');
    ui.pill.textContent = 'Connecting';
  }
  if (message) {
    ui.lastSync.textContent = message;
  }
}

function stampSync(label) {
  const now = new Date();
  ui.lastSync.textContent = `${label} · ${now.toLocaleTimeString()}`;
}

function renderOutput(target, data) {
  const node = ui.output[target];
  if (!node) {
    return;
  }
  node.classList.remove('output--empty');
  node.textContent = JSON.stringify(data, null, 2);
}

function renderError(target, error) {
  const node = ui.output[target];
  if (!node) {
    return;
  }
  node.classList.remove('output--empty');
  node.textContent = JSON.stringify(
    {
      ok: false,
      kind: 'client_error',
      error: { message: String(error?.message || error) },
    },
    null,
    2,
  );
}

function parseJson(text, fallback) {
  const source = (text || '').trim();
  if (!source) {
    return fallback;
  }
  return JSON.parse(source);
}

function activateView(viewId) {
  state.activeView = viewId;
  for (const item of ui.navItems) {
    item.classList.toggle('is-active', item.dataset.view === viewId);
  }
  for (const panel of ui.panels) {
    panel.classList.toggle('is-active', panel.dataset.panel === viewId);
  }
}

async function loadHealth() {
  setConnection(null, ui.lastSync.textContent);
  try {
    const data = await api.health();
    renderOutput('health', data);
    setConnection(true, ui.lastSync.textContent);
    stampSync('Health loaded');
  } catch (error) {
    renderError('health', error);
    setConnection(false, `Health failed · ${new Date().toLocaleTimeString()}`);
  }
}

async function loadContracts() {
  try {
    const data = await api.contracts();
    renderOutput('health', data);
    stampSync('Contracts loaded');
  } catch (error) {
    renderError('health', error);
  }
}

async function loadSnapshot() {
  try {
    const snapshotId = document.getElementById('snapshot-id').value.trim() || 'workspace';
    const selector = parseJson(document.getElementById('snapshot-selector').value, {});
    const data = await api.snapshot(snapshotId, selector);
    renderOutput('snapshot', data);
    stampSync('Snapshot loaded');
  } catch (error) {
    renderError('snapshot', error);
  }
}

async function runQuery() {
  try {
    const name = document.getElementById('query-name').value.trim();
    const params = parseJson(document.getElementById('query-params').value, {});
    const data = await api.query(name, params);
    renderOutput('query', data);
    stampSync('Query executed');
  } catch (error) {
    renderError('query', error);
  }
}

async function runCommand() {
  try {
    const name = document.getElementById('command-name').value.trim();
    const payload = parseJson(document.getElementById('command-payload').value, {});
    const context = parseJson(document.getElementById('command-context').value, {});
    const idempotencyKey = document.getElementById('command-idempotency').value.trim();
    const data = await api.command(name, payload, context, idempotencyKey || undefined);
    renderOutput('command', data);
    stampSync('Command submitted');
  } catch (error) {
    renderError('command', error);
  }
}

async function pollEvents() {
  try {
    const data = await api.events(state.eventsCursor);
    const events = Array.isArray(data.events) ? data.events : [];
    if (events.length > 0) {
      state.eventsCursor = events[events.length - 1].sequence || state.eventsCursor;
      renderOutput('events', {
        cursor: state.eventsCursor,
        count: events.length,
        events,
      });
    } else if (ui.output.events.classList.contains('output--empty')) {
      renderOutput('events', { cursor: state.eventsCursor, count: 0, events: [] });
    }
    ui.eventsCursor.textContent = `Cursor: ${state.eventsCursor}`;
    stampSync('Events polled');
  } catch (error) {
    renderError('events', error);
  }
}

function toggleEventsAuto() {
  state.eventsAuto = !state.eventsAuto;
  const button = document.getElementById('btn-events-toggle');
  if (state.eventsAuto) {
    ui.eventsMode.textContent = 'Mode: Auto (5s)';
    button.textContent = 'Stop Auto Poll';
    state.eventsTimer = window.setInterval(() => {
      void pollEvents();
    }, 5000);
    void pollEvents();
  } else {
    ui.eventsMode.textContent = 'Mode: Manual';
    button.textContent = 'Start Auto Poll';
    if (state.eventsTimer) {
      window.clearInterval(state.eventsTimer);
      state.eventsTimer = null;
    }
  }
}

function clearEvents() {
  ui.output.events.classList.add('output--empty');
  ui.output.events.textContent = 'No events yet.';
  state.eventsCursor = 0;
  ui.eventsCursor.textContent = 'Cursor: 0';
}

function bind() {
  for (const item of ui.navItems) {
    item.addEventListener('click', () => activateView(item.dataset.view || 'health'));
  }

  document.getElementById('btn-health').addEventListener('click', () => {
    void loadHealth();
  });
  document.getElementById('btn-contracts').addEventListener('click', () => {
    void loadContracts();
  });
  document.getElementById('btn-snapshot').addEventListener('click', () => {
    void loadSnapshot();
  });
  document.getElementById('btn-query').addEventListener('click', () => {
    void runQuery();
  });
  document.getElementById('btn-command').addEventListener('click', () => {
    void runCommand();
  });
  document.getElementById('btn-events-once').addEventListener('click', () => {
    void pollEvents();
  });
  document.getElementById('btn-events-toggle').addEventListener('click', toggleEventsAuto);
  document.getElementById('btn-events-clear').addEventListener('click', clearEvents);
  ui.refreshAll.addEventListener('click', () => {
    void loadHealth();
    void loadSnapshot();
    void runQuery();
  });
}

function init() {
  activateView(state.activeView);
  bind();
  setConnection(null, 'Booting shell...');
  void loadHealth();
}

init();

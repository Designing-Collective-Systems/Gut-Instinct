import './_.html';
import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { FlowRouter } from 'meteor/kadira:flow-router'; // optional (not used below)

// --- lightweight overlay (created entirely via JS) ---
let __overlayEl = null;

function showOverlay(msg = 'Generating visualization…') {
  if (__overlayEl) return;
  __overlayEl = document.createElement('div');
  __overlayEl.id = 'loadingOverlay';
  __overlayEl.setAttribute('aria-live', 'polite');
  __overlayEl.setAttribute('aria-busy', 'true');
  __overlayEl.style.cssText = [
    'position:fixed', 'inset:0', 'background:rgba(0,0,0,0.45)',
    'display:flex', 'align-items:center', 'justify-content:center',
    'z-index:9999'
  ].join(';');

  const card = document.createElement('div');
  card.style.cssText = [
    'background:#111', 'padding:24px 28px', 'border-radius:16px',
    'box-shadow:0 10px 30px rgba(0,0,0,0.4)',
    'display:flex', 'flex-direction:column', 'align-items:center',
    'min-width:260px'
  ].join(';');

  // SVG spinner (self-animated; no CSS keyframes needed)
  const spinner = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  spinner.setAttribute('width', '64');
  spinner.setAttribute('height', '64');
  spinner.setAttribute('viewBox', '0 0 50 50');
  spinner.innerHTML = `
    <circle cx="25" cy="25" r="20" fill="none" stroke="#e5e7eb" stroke-width="6" opacity="0.6"/>
    <path d="M25 5 a20 20 0 0 1 0 40" fill="none" stroke="#3b82f6" stroke-width="6" stroke-linecap="round">
      <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/>
    </path>
  `;

  const text = document.createElement('div');
  text.textContent = msg;
  text.style.cssText = 'margin-top:14px;color:#fff;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial,"Noto Sans";font-size:15px';

  card.appendChild(spinner);
  card.appendChild(text);
  __overlayEl.appendChild(card);
  document.body.appendChild(__overlayEl);
}

function hideOverlay() {
  if (__overlayEl && __overlayEl.parentNode) {
    __overlayEl.parentNode.removeChild(__overlayEl);
  }
  __overlayEl = null;
}

Template.gaQuestions.onCreated(function () {
  // no-op
});

Template.gaQuestions.events({
  'click #seeViz': function (event) {
    event.preventDefault();
    console.log('Button clicked!');

    const variable1 = document.getElementById('variable1').value.trim();
    const variable2 = document.getElementById('variable2').value.trim();

    console.log('Variable 1:', variable1);
    console.log('Variable 2:', variable2);

    if (!variable1 || !variable2) {
      alert('Please enter both variables before proceeding.');
      return false;
    }

    // lock UI + show overlay
    const btn = event.currentTarget;
    btn.setAttribute('aria-disabled', 'true');
    btn.style.pointerEvents = 'none';
    btn.style.opacity = '0.7';
    showOverlay('Generating visualization…');

    console.log('Calling Meteor method: runPythonVisualization');
    Meteor.call('runPythonVisualization', { variable1, variable2 }, (error, result) => {
      // always unlock + hide loader
      btn.removeAttribute('aria-disabled');
      btn.style.pointerEvents = '';
      btn.style.opacity = '';
      hideOverlay();

      if (error) {
        console.error('Error running visualization:', error);
        alert('Error generating visualization: ' + (error.reason || error.message || 'Unknown error'));
        return;
      }

      console.log('Python script setup successful:', result);

      // Navigate to dynamic route that serves the freshly created HTML
      const timestamp = Date.now();
      const dynamicUrl = `/standalone-viz/visualization.html?var1=${encodeURIComponent(variable1)}&var2=${encodeURIComponent(variable2)}&t=${timestamp}`;
      console.log('Navigating to dynamic visualization URL:', dynamicUrl);

      // small delay to ensure any final DOM flush
      setTimeout(() => { window.location.href = dynamicUrl; }, 100);
    });

    return false;
  }
});

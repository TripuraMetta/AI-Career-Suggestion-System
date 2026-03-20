/* ═══════════════════════════════════════════════
   AI Career Suggestion System — Validation & UI
   ═══════════════════════════════════════════════ */

$(document).ready(function () {

  /* ── Tab Toggle (Manual Skills / Resume Upload) ── */
  let activeTab = 'manual';

  window.switchTab = function (tab) {
    activeTab = tab;
    $('#tab-manual, #tab-resume').removeClass('active');
    $('#tab-' + tab).addClass('active');
    if (tab === 'manual') {
      $('#manual-section').show();
      $('#resume-section').hide();
      $('#resume-file').val('');
      $('#file-chosen').text('');
    } else {
      $('#manual-section').hide();
      $('#resume-section').show();
      $('#skills-input').val('');
    }
    clearErrors();
  };

  /* ── Drag & Drop Upload Zone ──────────────────── */
  const zone = document.getElementById('upload-zone');
  if (zone) {
    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) {
        setFileInput(file);
      }
    });
    zone.addEventListener('click', function () {
      $('#resume-file').click();
    });
  }

  $('#resume-file').on('change', function () {
    const file = this.files[0];
    if (file) setFileInput(file);
  });

  function setFileInput(file) {
    if (!file.name.endsWith('.docx')) {
      showFieldError('resume-error', 'Only .docx files are supported.');
      $('#file-chosen').text('');
      return;
    }
    // Assign to actual input via DataTransfer
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById('resume-file').files = dt.files;
    $('#file-chosen').text('📄 ' + file.name);
    clearFieldError('resume-error');
  }

  /* ── Skill Tag Preview ────────────────────────── */
  $('#skills-input').on('input', function () {
    const raw = $(this).val();
    const tags = raw.split(',').map(s => s.trim()).filter(Boolean);
    let html = '';
    tags.forEach(function (t) {
      if (t) html += '<span class="skill-tag">' + escapeHtml(t) + '</span>';
    });
    $('#skill-preview').html(html);
  });

  function escapeHtml(t) {
    return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  /* ── Form Validation ──────────────────────────── */
  $('#career-form').on('submit', function (e) {
    clearErrors();
    let valid = true;

    // Name
    const name = $('#name-input').val().trim();
    if (!name) {
      showFieldError('name-error', 'Please enter your name.');
      valid = false;
    } else if (name.length < 2) {
      showFieldError('name-error', 'Name must be at least 2 characters.');
      valid = false;
    }

    // Skills or Resume
    if (activeTab === 'manual') {
      const skills = $('#skills-input').val().trim();
      if (!skills) {
        showFieldError('skills-error', 'Please enter at least one skill.');
        valid = false;
      } else {
        const skillList = skills.split(',').map(s => s.trim()).filter(Boolean);
        if (skillList.length < 1) {
          showFieldError('skills-error', 'Enter valid comma-separated skills.');
          valid = false;
        }
      }
    } else {
      const file = $('#resume-file')[0].files[0];
      if (!file) {
        showFieldError('resume-error', 'Please upload a .docx resume.');
        valid = false;
      } else if (!file.name.endsWith('.docx')) {
        showFieldError('resume-error', 'Only .docx files are supported.');
        valid = false;
      }
    }

    if (!valid) {
      e.preventDefault();
      $('html, body').animate({ scrollTop: $('.error-box:visible').offset()?.top - 80 || 0 }, 300);
      return;
    }

    // Show loading state
    $('#submit-btn').prop('disabled', true);
    $('#submit-text').text('Analyzing...');
    $('#submit-spinner').show();
  });

  /* ── Error Helpers ────────────────────────────── */
  function showFieldError(id, msg) {
    $('#' + id).html('<span>⚠</span> ' + msg).show();
  }
  function clearFieldError(id) {
    $('#' + id).hide().html('');
  }
  function clearErrors() {
    $('.error-box').hide().html('');
  }

  /* ── Confidence Bar Animation (Result Page) ───── */
  const fill = document.querySelector('.confidence-fill');
  if (fill) {
    const target = fill.getAttribute('data-width');
    setTimeout(function () {
      fill.style.width = target + '%';
    }, 300);
  }

  /* ── History: Confirm Clear ───────────────────── */
  $('#clear-history-btn').on('click', function (e) {
    if (!confirm('Are you sure you want to delete all history? This cannot be undone.')) {
      e.preventDefault();
    }
  });

});

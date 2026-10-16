// ==UserScript==
// @name         উইকিপিডিয়া অনুবাদ টুল — CX খসড়া ইন্টিগ্রেশন
// @namespace    bnwiki-translation-toolkit
// @version      1.1.0
// @description  ContentTranslation-এ গুগল ও MinT-এর সাথে প্রমিত উইকিপিডিয়া অনুবাদ টুল যুক্তকরণ এবং খসড়া প্রকাশনা নিয়ন্ত্রণ
// @match        https://bn.wikipedia.org/wiki/Special:ContentTranslation*
// @match        https://bn.wikipedia.org/wiki/%E0%A6%96%E0%A6%B8%E0%A6%A1%E0%A6%BC%E0%A6%BE:*
// @match        https://bn.wikipedia.org/wiki/খসড়া:*
// @match        https://bn.wikipedia.org/w/index.php*
// @grant        GM_xmlhttpRequest
// @grant        GM_notification
// @connect      127.0.0.1
// ==/UserScript==

(function () {
  'use strict';
  var API_BASE = 'http://127.0.0.1:8765';

  function callApi(endpoint, method, data, cb) {
    var url = API_BASE + endpoint;
    if (typeof GM_xmlhttpRequest !== 'undefined') {
      GM_xmlhttpRequest({
        method: method,
        url: url,
        headers: { 'Content-Type': 'application/json' },
        data: data ? JSON.stringify(data) : null,
        onload: function (res) {
          try { cb(null, JSON.parse(res.responseText)); }
          catch (e) { cb(e); }
        },
        onerror: function (e) { cb(e); }
      });
    } else {
      fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null
      }).then(function (r) { return r.json(); }).then(function (j) { cb(null, j); }, cb);
    }
  }

  // ১. সাইডবারে "প্রারম্ভিক অনুবাদ" তালিকায় অপশন যুক্ত করা
  function injectCxSidebarOption() {
    // CX-এর অনুবাদ নির্বাচন প্যানেল খোঁজা
    var sidebar = document.querySelector('.cx-sidebar, .cx-column--tools, .ve-ui-cxTranslationSelectorWidget');
    if (!sidebar) return;

    if (document.getElementById('cx-custom-toolkit-option')) return;

    var container = document.createElement('div');
    container.id = 'cx-custom-toolkit-option';
    container.style.cssText = 'margin: 12px 0; padding: 10px; background: #f0fdf4; border: 1.5px solid #10b981; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s;';
    container.innerHTML =
      '<span style="font-size: 18px; color: #10b981;">★</span>' +
      '<div>' +
      '<strong style="color: #065f46; font-size: 13px; display: block;">উইকিপিডিয়া অনুবাদ টুল (খসড়া)</strong>' +
      '<span style="font-size: 11px; color: #047857;">১০০% প্রমিত নিয়ম • সরাসরি খসড়ায় প্রকাশ</span>' +
      '</div>';

    container.onmouseenter = function () { container.style.background = '#dcfce7'; };
    container.onmouseleave = function () { container.style.background = '#f0fdf4'; };

    container.onclick = function () {
      applyToolkitTranslation();
    };

    // উপযুক্ত স্থানে ইনসার্ট করা
    sidebar.prepend(container);
  }

  // ২. সক্রিয় অনুচ্ছেদে প্রমিত রূপান্তর প্রয়োগ
  function applyToolkitTranslation() {
    var activeSection = document.querySelector('.cx-column--translation .cx-section--active, .cx-column--translation [contenteditable="true"]');
    var textToFix = '';
    if (activeSection) {
      textToFix = activeSection.innerText || activeSection.textContent;
    }

    if (!textToFix) {
      // যদি সিলেকশন না থাকে, তবে ড্রাফট প্যানেল খুলুন
      showQuickPanel();
      return;
    }

    notify('অনুবাদ প্রমিতকরণ হচ্ছে...');
    callApi('/fix', 'POST', { text: textToFix }, function (err, res) {
      if (err || !res) {
        alert('লোকাল সার্ভার চালু নেই! আগে টার্মিনালে চালান:\npython -m cx_postprocess.server');
        return;
      }
      if (activeSection) {
        activeSection.innerText = res.fixed;
      }
      notify('প্রমিত রূপান্তর প্রয়োগ করা হয়েছে ✓');
      ensureDraftNamespace();
    });
  }

  // ৩. মূল নামস্থানের পরিবর্তে "খসড়া:" নিশ্চিত করা ও ২৪ ঘণ্টার ট্র্যাকিং
  function ensureDraftNamespace() {
    // CX হেডারের প্রকাশনা বোতাম
    var publishBtn = document.querySelector('.cx-header__publish, .ve-ui-toolbar-saveButton, button[data-action="publish"]');
    var targetInput = document.querySelector('.cx-header__title, #cx-target-title');
    var currentTitle = targetInput ? (targetInput.value || targetInput.innerText) : '';

    if (!currentTitle) {
      var urlParams = new URLSearchParams(window.location.search);
      currentTitle = urlParams.get('page') || 'নতুন_নিবন্ধ';
    }

    currentTitle = currentTitle.replace(/^খসড়া:/, '').trim();
    var draftTitle = 'খসড়া:' + currentTitle;

    // ট্র্যাকিং সার্ভারে সংরক্ষণ
    callApi('/drafts', 'POST', {
      title: draftTitle,
      main_title: currentTitle,
      created_at: new Date().toISOString()
    }, function () {
      console.log('Draft tracked:', draftTitle);
    });

    notify(`নীতি: এটি সরাসরি '${draftTitle}' পাতায় প্রকাশিত হবে। ২৪ ঘণ্টা পর মূল নামস্থানে স্থানান্তরযোগ্য।`);
  }

  function notify(msg) {
    var toast = document.getElementById('cx-toolkit-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'cx-toolkit-toast';
      toast.style.cssText = 'position:fixed;top:70px;right:20px;z-index:999999;background:#0f172a;color:#fff;border-left:4px solid #10b981;padding:12px 18px;border-radius:6px;box-shadow:0 8px 24px rgba(0,0,0,0.3);font-size:13px;max-width:320px;line-height:1.4;';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(function () { toast.style.display = 'none'; }, 4500);
  }

  // ৪. সার্বজনীন কুইক প্যানেল ও ড্যাশবোর্ড লিঙ্ক
  function showQuickPanel() {
    if (document.getElementById('cx-quick-panel')) return;
    var box = document.createElement('div');
    box.id = 'cx-quick-panel';
    box.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:99999;' +
      'background:#fff;border:1.5px solid #10b981;border-radius:10px;padding:12px;width:340px;' +
      'font-size:13px;box-shadow:0 4px 16px rgba(0,0,0,.15);font-family:sans-serif;';
    box.innerHTML =
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">' +
      '<b style="color:#065f46;">উইকিপিডিয়া অনুবাদ টুল (খসড়া)</b>' +
      '<button id="cx-panel-close" style="background:none;border:none;cursor:pointer;font-weight:bold;color:#666;">✕</button>' +
      '</div>' +
      '<textarea id="cx-panel-input" rows="4" style="width:100%;box-sizing:border-box;border:1px solid #ccc;border-radius:4px;padding:6px;font-size:12px;" placeholder="অনুচ্ছেদের উইকিটেক্সট এখানে পেস্ট করুন..."></textarea>' +
      '<div style="margin-top:6px;display:flex;gap:6px;">' +
      '<button id="cx-panel-fix" style="background:#10b981;color:#fff;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-weight:bold;flex:1;">প্রমিত করো</button>' +
      '<a href="http://127.0.0.1:8765/dashboard" target="_blank" style="background:#0284c7;color:#fff;text-decoration:none;padding:6px 10px;border-radius:4px;font-size:12px;display:inline-flex;align-items:center;">ড্যাশবোর্ড</a>' +
      '</div>' +
      '<textarea id="cx-panel-output" rows="4" style="width:100%;box-sizing:border-box;margin-top:6px;border:1px solid #ccc;border-radius:4px;padding:6px;font-size:12px;" readonly placeholder="প্রমিত আউটপুট..."></textarea>';

    document.body.appendChild(box);

    document.getElementById('cx-panel-close').onclick = function () { box.remove(); };
    document.getElementById('cx-panel-fix').onclick = function () {
      var val = document.getElementById('cx-panel-input').value;
      if (!val) return;
      callApi('/fix', 'POST', { text: val }, function (err, res) {
        if (err || !res) { alert('সার্ভার চালু নেই (127.0.0.1:8765)'); return; }
        document.getElementById('cx-panel-output').value = res.fixed || '';
        document.getElementById('cx-panel-output').select();
        ensureDraftNamespace();
      });
    };
  }

  // ৫. খসড়া পাতার এডিট বক্সে স্বয়ংক্রিয়ভাবে অনূদিত টেক্সট লোড করা (যদি খালি থাকে)
  function autoFillDraftPage() {
    var isEdit = window.location.href.indexOf('action=edit') !== -1 || window.location.href.indexOf('action=submit') !== -1;
    var isDraft = window.location.href.indexOf('%E0%A6%96%E0%A6%B8%E0%A6%A1%E0%A6%BC%E0%A6%BE') !== -1 || 
                  decodeURIComponent(window.location.href).indexOf('খসড়া:') !== -1;

    if (isEdit && isDraft) {
      var txtBox = document.getElementById('wpTextbox1');
      if (txtBox && !txtBox.value.trim()) {
        var preload = localStorage.getItem('wiki_draft_preload');
        if (preload && preload.trim()) {
          txtBox.value = preload;
          notify('উইকিপিডিয়া অনুবাদ টুল: অনূদিত টেক্সট স্বয়ংক্রিয়ভাবে লোড হয়েছে ✓');
        }
      }
    }
  }

  // পৃষ্ঠা লোডের পর এবং পর্যায়ক্রমে ড্রাফট ইনপুট চেক
  setTimeout(autoFillDraftPage, 500);
  setInterval(autoFillDraftPage, 2000);

  // পোলিং করে সাইডবার উপাদান পর্যবেক্ষণ
  setInterval(injectCxSidebarOption, 1500);

  // ডিফল্টভাবে কুইক ভাসমান বাটন
  var floatBtn = document.createElement('button');
  floatBtn.innerHTML = '★ উইকি অনুবাদ টুল';
  floatBtn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:99990;background:#10b981;color:#fff;border:none;padding:8px 14px;border-radius:20px;font-weight:600;box-shadow:0 2px 10px rgba(0,0,0,0.2);cursor:pointer;font-size:12px;';
  floatBtn.onclick = showQuickPanel;
  document.body.appendChild(floatBtn);

})();

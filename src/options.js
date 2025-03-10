function loadOptions() {
  return utils.getOptions().then((options) => {
    document.querySelector('#userBlacklist textarea').value = options.userBlacklist;
    document.querySelector('#userWhitelist textarea').value = options.userWhitelist;
    document.querySelector('#webBlacklists textarea').value = options.webBlacklists;
    document.querySelector('#transformRules textarea').value = options.transformRules;
    document.querySelector('#suppressHistory input').checked = options.suppressHistory;
    document.querySelector('#showLinkMarkers input').checked = options.showLinkMarkers;
    document.querySelector('#showContextMenuCommands input').checked = options.showContextMenuCommands;
    document.querySelector('#quickContextMenuCommands input').checked = options.quickContextMenuCommands;
    document.querySelector('#showUnblockButton input').checked = options.showUnblockButton;

    return browser.runtime.sendMessage({
      cmd: 'getMergedBlacklist',
    }).then((blacklist) => {
      document.querySelector('#allBlacklist textarea').value = blacklist;
    });
  });
}

function saveOptions() {
  const userBlacklist = document.querySelector('#userBlacklist textarea').value;
  const userWhitelist = document.querySelector('#userWhitelist textarea').value;
  const webBlacklists = document.querySelector('#webBlacklists textarea').value;
  const transformRules = document.querySelector('#transformRules textarea').value;
  let suppressHistory = document.querySelector('#suppressHistory input').checked;
  const showLinkMarkers = document.querySelector('#showLinkMarkers input').checked;
  const showContextMenuCommands = document.querySelector('#showContextMenuCommands input').checked;
  const quickContextMenuCommands = document.querySelector('#quickContextMenuCommands input').checked;
  const showUnblockButton = document.querySelector('#showUnblockButton input').checked;

  // Firefox < 54: No browser.permissions.
  //
  // @FIXME:
  // Firefox < 56: the request dialog prompts repeatedly even if the
  // permissions are already granted. Checking permissions.contains() in
  // prior doesn't work as Promise.then() breaks tracing of the user input
  // event handler and makes the request always fail (for Firefox < 60).
  // https://bugzilla.mozilla.org/show_bug.cgi?id=1398833
  return (() => {
    if (!suppressHistory || !browser.permissions) {
      return Promise.resolve(false);
    }

    return browser.permissions.request({permissions: ['history']}).catch((ex) => {
      console.error(ex);
      return false;
    });
  })().then((granted) => {
    if (!granted) {
      suppressHistory = document.querySelector('#suppressHistory input').checked = false;
    }
  }).then(() => {
    return browser.runtime.sendMessage({
      cmd: 'updateOptions',
      args: {
        userBlacklist,
        userWhitelist,
        webBlacklists,
        transformRules,
        suppressHistory,
        showLinkMarkers,
        showContextMenuCommands,
        quickContextMenuCommands,
        showUnblockButton,
      },
    });
  });
}

function onReset(event) {
  event.preventDefault();
  if (!confirm(utils.lang("resetConfirm"))) {
    return;
  }
  return utils.clearOptions().then(() => {
    return loadOptions();
  });
}

function onSubmit(event) {
  event.preventDefault();
  return saveOptions().then(() => {
    return utils.back();
  });
}


function init(event) {
  utils.loadLanguages(document);

  // hide some options if contextMenus is not available
  // (e.g. Firefox for Android)
  if (!browser.contextMenus || utils.userAgent.soup.has('mobile')) {
    document.querySelector('#showContextMenuCommands').hidden = true;
    document.querySelector('#quickContextMenuCommands').hidden = true;
  }

  // hide some options if browser.history is not available
  // Firefox < 55: no browser.permissions, and permissions listed in
  // "optional_permissions" are ignored.
  // Chromium mobile (e.g. Kiwi): cannot call browser.permissions.request()
  // Firefox for Android: no browser.history. However, we cannot simply check
  // browser.history as it's undefined before granted permission.
  if (!browser.permissions && !browser.history || utils.userAgent.soup.has('mobile')) {
    document.querySelector('#suppressHistory').hidden = true;
  }

  loadOptions(); // async

  try {
    const url = new URL(location.href).searchParams.get('from');
    if (url) {
      const urlRegex = `/^${utils.escapeRegExp(url, true)}$/`;
      document.querySelector('#urlInfo').textContent = utils.lang('urlInfo', [url, urlRegex]);
    }
  } catch (ex) {
    console.error(ex);
  }

  document.querySelector('#resetButton').addEventListener('click', onReset);
  document.querySelector('#submitButton').addEventListener('click', onSubmit);
}

document.addEventListener('DOMContentLoaded', init);

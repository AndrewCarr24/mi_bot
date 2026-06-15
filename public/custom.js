// Toggle the `cl-suppress-login-flash` class on <html> based on the
// current route. When set, custom.css fades the body to opacity 0 and
// shows a centered spinner instead — hiding Chainlit's "Login to access
// the app" intermediate screen that flashes during the header-auth
// handshake (see custom.css for the full sequence).
//
// We listen to pushState / popstate AND poll briefly because Chainlit's
// router occasionally swaps routes without firing those events.

(function () {
  const SUPPRESS_CLASS = "cl-suppress-login-flash";
  const LOGIN_PATH_RE = /\/chat\/login\/?$/;

  function update() {
    const isLogin = LOGIN_PATH_RE.test(location.pathname);
    document.documentElement.classList.toggle(SUPPRESS_CLASS, isLogin);
  }

  update();

  const origPushState = history.pushState;
  history.pushState = function () {
    origPushState.apply(this, arguments);
    update();
  };
  const origReplaceState = history.replaceState;
  history.replaceState = function () {
    origReplaceState.apply(this, arguments);
    update();
  };
  window.addEventListener("popstate", update);

  // Fallback poll for SPA navigations that bypass pushState/popstate.
  // Cheap (a string compare every 100ms) and self-clears after the user
  // navigates past /chat/login the first time we see them past it for
  // 5 seconds (i.e. the flash window has clearly elapsed).
  let last = location.pathname;
  let pastLoginSince = null;
  const intervalId = setInterval(() => {
    if (location.pathname !== last) {
      last = location.pathname;
      update();
    }
    if (!LOGIN_PATH_RE.test(location.pathname)) {
      pastLoginSince = pastLoginSince ?? Date.now();
      if (Date.now() - pastLoginSince > 5000) {
        clearInterval(intervalId);
      }
    } else {
      pastLoginSince = null;
    }
  }, 100);
})();

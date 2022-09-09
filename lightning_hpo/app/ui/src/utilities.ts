export function getUrl() {
  let url = window.location != window.parent.location ? document.referrer : document.location.href;
  url = url.replace(/\/$/, '').replace('/view/undefined', '');
  return url;
}

export function getAppId() {
  let app_id = getUrl()
    .replace(/(^\w+:|^)\/\//, '')
    .split('.')[0];
  app_id = app_id === '127' ? 'localhost' : app_id;
  return app_id;
}

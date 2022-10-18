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

function zeroPad(num: number, places: number) {
  const zero = places - num.toString().length + 1;
  return Array(+(zero > 0 && zero)).join('0') + num;
}

export function formatDurationFrom(start_time: number) {
  return formatDurationStartEnd(new Date().getTime() / 1000, start_time);
}

export function formatDurationStartEnd(end_time: number, start_time: number) {
  let duration = end_time - start_time;
  const hours = Math.floor(duration / 1440);
  duration = duration - hours * 1440;
  const minutes = Math.floor(duration / 60);
  duration = duration - minutes * 60;
  const seconds = Math.floor(duration);
  return `${zeroPad(hours, 2)}:${zeroPad(minutes, 2)}:${zeroPad(seconds, 2)}`;
}

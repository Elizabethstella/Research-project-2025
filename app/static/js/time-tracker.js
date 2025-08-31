let seconds = 0;
let interval;
function initTimeTracker(topicId) {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") sendTime(topicId);
  });
  interval = setInterval(() => { seconds+=20; sendTime(topicId); }, 20000);
  window.addEventListener("beforeunload", () => { sendTime(topicId,true); });
}
function sendTime(topicId, unload=false) {
  if(seconds<=0) return;
  navigator.sendBeacon("/api/track_time", JSON.stringify({topic_id: topicId, seconds: seconds}));
  seconds=0;
}

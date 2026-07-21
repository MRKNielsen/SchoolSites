/* ============================================================
   hub.js — shared behaviour for course-hub pages
   - Highlights the current week: <div class="week" data-start="YYYY-MM-DD">
     inside #weeks; optional data-end="YYYY-MM-DD" on #weeks bounds the
     last week (defaults to 7 days after its start).
   - Marks timeline milestones: .mile[data-date] gets .done when past,
     the first upcoming one gets .next.
   - Countdown: <span class="countdown" data-to="YYYY-MM-DD"> shows
     "N days away" / "underway".
   ============================================================ */
(function () {
  "use strict";
  const today = new Date(); today.setHours(0, 0, 0, 0);

  const weeksWrap = document.getElementById("weeks");
  const weeks = weeksWrap ? Array.from(weeksWrap.querySelectorAll(".week[data-start]")) : [];
  weeks.forEach((w, i) => {
    const start = new Date(w.dataset.start + "T00:00:00");
    const next = weeks[i + 1]
      ? new Date(weeks[i + 1].dataset.start + "T00:00:00")
      : (weeksWrap.dataset.end
          ? new Date(weeksWrap.dataset.end + "T00:00:00")
          : new Date(start.getTime() + 7 * 86400000));
    if (today >= start && today < next) w.classList.add("current");
  });
  const cur = document.querySelector(".week.current");
  if (cur) setTimeout(() => cur.scrollIntoView({ behavior: "smooth", block: "center" }), 300);

  let nextMarked = false;
  document.querySelectorAll(".mile[data-date]").forEach(m => {
    const d = new Date(m.dataset.date + "T00:00:00");
    if (d < today) m.classList.add("done");
    else if (!nextMarked) { m.classList.add("next"); nextMarked = true; }
  });

  document.querySelectorAll(".countdown[data-to]").forEach(el => {
    const target = new Date(el.dataset.to + "T00:00:00");
    const days = Math.ceil((target - today) / 86400000);
    el.textContent = days > 0 ? days + " days away" : "underway";
  });
})();

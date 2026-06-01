// 车辆模拟数据
const CARS = [
  { id: 1, name: "大众 朗逸", type: "经济型", price: 99, emoji: "🚗", bg: "#dbeafe", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 2, name: "丰田 卡罗拉", type: "经济型", price: 109, emoji: "🚙", bg: "#dcfce7", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 3, name: "本田 雅阁", type: "舒适型", price: 159, emoji: "🚘", bg: "#fef9c3", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 4, name: "大众 帕萨特", type: "舒适型", price: 169, emoji: "🚖", bg: "#fae8ff", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 5, name: "丰田 汉兰达", type: "SUV", price: 259, emoji: "🚐", bg: "#ffedd5", seats: 7, trans: "自动", fuel: "汽油" },
  { id: 6, name: "本田 CR-V", type: "SUV", price: 219, emoji: "🚙", bg: "#e0e7ff", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 7, name: "奔驰 E 级", type: "豪华型", price: 599, emoji: "🏎️", bg: "#f1f5f9", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 8, name: "宝马 5 系", type: "豪华型", price: 569, emoji: "🏎️", bg: "#e2e8f0", seats: 5, trans: "自动", fuel: "汽油" },
  { id: 9, name: "特斯拉 Model 3", type: "新能源", price: 299, emoji: "⚡", bg: "#ccfbf1", seats: 5, trans: "自动", fuel: "纯电" },
  { id: 10, name: "比亚迪 汉 EV", type: "新能源", price: 269, emoji: "🔋", bg: "#d1fae5", seats: 5, trans: "自动", fuel: "纯电" },
  { id: 11, name: "五菱 宏光 MINI", type: "经济型", price: 79, emoji: "🚗", bg: "#fee2e2", seats: 4, trans: "自动", fuel: "纯电" },
  { id: 12, name: "理想 L8", type: "SUV", price: 389, emoji: "🚐", bg: "#ede9fe", seats: 6, trans: "自动", fuel: "增程" },
];

let currentFilter = "all";
let selectedCar = null;

const grid = document.getElementById("carGrid");
const emptyState = document.getElementById("emptyState");

// 渲染车辆卡片
function renderCars() {
  const list = currentFilter === "all" ? CARS : CARS.filter((c) => c.type === currentFilter);
  grid.innerHTML = list
    .map(
      (c) => `
    <article class="car-card">
      <div class="car-thumb" style="background:${c.bg}">${c.emoji}</div>
      <div class="car-body">
        <div class="car-name">${c.name}</div>
        <span class="car-tag">${c.type}</span>
        <div class="car-meta">
          <span>👥 ${c.seats} 座</span>
          <span>⚙️ ${c.trans}</span>
          <span>⛽ ${c.fuel}</span>
        </div>
        <div class="car-foot">
          <div class="car-price">¥${c.price}<small>/天</small></div>
          <button class="btn btn-primary" data-book="${c.id}">立即预订</button>
        </div>
      </div>
    </article>`
    )
    .join("");
  emptyState.hidden = list.length !== 0;
}

// 筛选
document.getElementById("filters").addEventListener("click", (e) => {
  const btn = e.target.closest(".chip");
  if (!btn) return;
  document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  btn.classList.add("active");
  currentFilter = btn.dataset.type;
  renderCars();
});

// 顶部搜索：同步车型筛选并滚动到列表
document.getElementById("searchForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const pickup = document.getElementById("pickup").value;
  const dropoff = document.getElementById("dropoff").value;
  if (pickup && dropoff && new Date(dropoff) <= new Date(pickup)) {
    showToast("还车时间需晚于取车时间");
    return;
  }
  const type = document.getElementById("carType").value;
  currentFilter = type;
  document.querySelectorAll(".chip").forEach((c) =>
    c.classList.toggle("active", c.dataset.type === type)
  );
  renderCars();
  document.getElementById("cars").scrollIntoView({ behavior: "smooth" });
  showToast("已为你筛选 " + (type === "all" ? "全部" : type) + " 车辆");
});

// 预订弹窗
const modal = document.getElementById("bookingModal");
const modalCar = document.getElementById("modalCar");
const bkDays = document.getElementById("bkDays");
const bkTotal = document.getElementById("bkTotal");

grid.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-book]");
  if (!btn) return;
  selectedCar = CARS.find((c) => c.id === Number(btn.dataset.book));
  openModal();
});

function openModal() {
  modalCar.innerHTML = `<strong>${selectedCar.emoji} ${selectedCar.name}</strong>（${selectedCar.type}） · ¥${selectedCar.price}/天`;
  bkDays.value = 1;
  updateTotal();
  modal.hidden = false;
}

function closeModal() {
  modal.hidden = true;
}

function updateTotal() {
  const days = Math.max(1, Number(bkDays.value) || 1);
  bkTotal.textContent = "¥" + days * selectedCar.price;
}

bkDays.addEventListener("input", updateTotal);

modal.addEventListener("click", (e) => {
  if (e.target.hasAttribute("data-close")) closeModal();
});

document.getElementById("bookingForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const days = Math.max(1, Number(bkDays.value) || 1);
  closeModal();
  showToast(`预订成功！${selectedCar.name}，共 ${days} 天，合计 ¥${days * selectedCar.price}`);
});

// 登录占位
document.getElementById("loginBtn").addEventListener("click", () =>
  showToast("登录功能为演示占位～")
);

// 提示条
let toastTimer;
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.hidden = true), 2600);
}

// 默认取还车时间（今天 10:00 / 明天 10:00）
function initDates() {
  const fmt = (d) => {
    const p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
  };
  const now = new Date();
  now.setHours(10, 0, 0, 0);
  const tmr = new Date(now);
  tmr.setDate(tmr.getDate() + 1);
  document.getElementById("pickup").value = fmt(now);
  document.getElementById("dropoff").value = fmt(tmr);
}

// 初始化
initDates();
renderCars();

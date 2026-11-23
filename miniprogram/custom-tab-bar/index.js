Component({
  data: {
    selected: 2,
    list: [
      { path: "/pages/diseases/diseases", text: "百科", icon: "📖" },
      { path: "/pages/history/history", text: "历史", icon: "⏱" },
      { path: "/pages/home/home", text: "首页", icon: "🏠" },
      { path: "/pages/stats/stats", text: "统计", icon: "📊" },
      { path: "/pages/detect/detect", text: "识别", icon: "📷" }
    ]
  },
  methods: {
    switchTab(e) {
      const path = e.currentTarget.dataset.path
      wx.switchTab({ url: path })
    }
  }
})

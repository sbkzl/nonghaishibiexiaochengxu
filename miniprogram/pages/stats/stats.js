const colors = ['#2b7a4b', '#e67e22', '#3498db', '#9b59b6', '#e74c3c', '#1abc9c']

Page({
  data: {
    pieData: [],
    barData: [],
    totalCount: 0,
    diseaseTypes: 0,
    baseUrl: "http://10.91.226.115:8000"
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
    }
    this.loadStats()
  },

  loadStats() {
    wx.request({
      url: this.data.baseUrl + "/history",
      success: (res) => {
        if (res.data.code !== 200) return
        const data = res.data.data
        const map = {}
        data.forEach(item => {
          const name = item.chinese_name || item.disease_name
          map[name] = (map[name] || 0) + 1
        })
        const entries = Object.entries(map)
        const total = entries.reduce((s, [, v]) => s + v, 0)

        const pieData = entries.map(([name, value], i) => {
          const c = colors[i % colors.length]
          return { name, value, color: c, dotStyle: 'background:' + c }
        })

        const barData = entries.map(([name, value], i) => {
          const c = colors[i % colors.length]
          const pct = (value / total * 100).toFixed(1)
          return { name, value, percent: pct, color: c, barStyle: 'width:' + pct + '%;background:' + c }
        })

        this.setData({
          pieData, barData,
          totalCount: total,
          diseaseTypes: entries.length
        })

        this.drawPie(pieData, total)
      }
    })
  },

  drawPie(pieData, total) {
    const query = wx.createSelectorQuery().in(this)
    query.select('.pie').boundingClientRect((rect) => {
      const size = rect.width || 300
      const center = size / 2
      const radius = size / 2 - 20
  
      const ctx = wx.createCanvasContext('pieCanvas', this)
      let startAngle = -Math.PI / 2
      const gap = 0.00
  
      pieData.forEach((item) => {
        const sliceAngle = (item.value / total) * Math.PI * 2
        ctx.beginPath()
        ctx.arc(center, center, radius, startAngle + gap, startAngle + sliceAngle - gap)
        ctx.lineTo(center, center) // 从中心切出去
        ctx.closePath()
        ctx.fillStyle = item.color
        ctx.fill()
        startAngle += sliceAngle
      })
  
      ctx.draw()
    }).exec()
  }  
})

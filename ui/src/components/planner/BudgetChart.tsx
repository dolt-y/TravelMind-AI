import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { LegendComponent, TitleComponent, TooltipComponent } from 'echarts/components'
import { init, use as registerECharts } from 'echarts/core'
import { ChartPie, WalletCards } from 'lucide-react'
import { useEffect, useMemo, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import type { TripBudget } from '../../types'

registerECharts([PieChart, CanvasRenderer, LegendComponent, TitleComponent, TooltipComponent])

interface BudgetChartProps {
  budget: TripBudget
}

function formatMoney(value: number, currency: string) {
  const amount = value.toLocaleString()
  return currency === 'CNY' ? `¥${amount}` : `${currency} ${amount}`
}

export function BudgetChart({ budget }: BudgetChartProps) {
  const { t } = useTranslation()
  const chartRef = useRef<HTMLDivElement>(null)
  const entries = useMemo(() => [
    { name: t('tripVisuals.budget.categories.attractions'), value: budget.attractions },
    { name: t('tripVisuals.budget.categories.hotels'), value: budget.hotels },
    { name: t('tripVisuals.budget.categories.meals'), value: budget.meals },
    { name: t('tripVisuals.budget.categories.transportation'), value: budget.transportation },
  ].filter((entry) => entry.value > 0), [budget.attractions, budget.hotels, budget.meals, budget.transportation, t])

  useEffect(() => {
    if (!chartRef.current || !entries.length) return
    const chart = init(chartRef.current)
    const totalText = formatMoney(budget.total, budget.currency)

    chart.setOption({
      color: ['#345f7a', '#d37a57', '#3d8067', '#c4893f'],
      title: {
        text: totalText,
        subtext: t('tripVisuals.budget.total'),
        left: 'center',
        top: '35%',
        textStyle: { color: '#18344a', fontSize: 22, fontWeight: 700 },
        subtextStyle: { color: '#708392', fontSize: 10 },
      },
      tooltip: {
        trigger: 'item',
        valueFormatter: (value: number) => formatMoney(value, budget.currency),
      },
      legend: {
        bottom: 6,
        left: 'center',
        icon: 'circle',
        itemWidth: 8,
        itemHeight: 8,
        itemGap: 14,
        textStyle: { color: '#425c70', fontSize: 10 },
      },
      series: [{
        type: 'pie',
        radius: ['46%', '68%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: { borderColor: '#fff', borderWidth: 3 },
        label: { show: false },
        emphasis: { scaleSize: 5 },
        data: entries,
      }],
    })

    // 图表跟随结果区域宽度变化，兼容侧栏和移动端布局切换。
    const observer = new ResizeObserver(() => chart.resize())
    observer.observe(chartRef.current)
    return () => {
      observer.disconnect()
      chart.dispose()
    }
  }, [budget.currency, budget.total, entries, t])

  return (
    <section className="result-visual result-visual--budget" aria-labelledby="budget-chart-title">
      <header className="result-visual__heading">
        <ChartPie size={22} aria-hidden="true" />
        <div>
          <h2 id="budget-chart-title">{t('tripVisuals.budget.title')}</h2>
        </div>
      </header>
      {entries.length ? (
        <div
          ref={chartRef}
          className="budget-chart__canvas"
          role="img"
          aria-label={t('tripVisuals.budget.aria', { total: formatMoney(budget.total, budget.currency) })}
        />
      ) : (
        <div className="budget-chart__empty">
          <WalletCards size={25} aria-hidden="true" />
          <span>{t('tripVisuals.budget.empty')}</span>
        </div>
      )}
    </section>
  )
}

import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  zh: {
    translation: {
      nav: { explore: '灵感探索', library: '我的资料', api: '开发接口', start: '开始规划', homeAria: 'TravelMind AI 首页', mainAria: '主导航' },
      status: { checking: '检查中', offline: '服务未连接', waiting: '等待配置', online: '服务可用', refresh: '刷新服务状态' },
      hero: {
        kicker: 'AI 智能行程规划', title: '发现世界的美好', copy: '让每一次出发，都从真实的旅行灵感开始。',
        cityLabel: '目的地', cityPlaceholder: '想去哪里？', preferenceLabel: '旅行偏好', preferencePlaceholder: '历史文化、美食、亲子…',
        submit: '开始规划', submitting: '正在整理', notes: '参考游记 {{count}} 篇', noteAria: '参考游记数量', languageAria: '结果语言',
      },
      language: { zh: '中文', en: 'English', ja: '日本語' },
      features: {
        aria: '旅行资料能力', plan: 'AI 智能规划', planSub: '从灵感到路线', custom: '个性化定制', customSub: '贴合你的偏好',
        trusted: '实时可信', trustedSub: '地图与天气资料', start: '一键出发', startSub: '保存你的发现',
      },
      error: { close: '关闭', missingCity: '请先填写目的地城市', enrichFailed: '景点资料已保存，天气和住宿资料暂时不可用', extractionFailed: '景点提取失败，请稍后重试' },
      loading: { title: '正在探索 {{city}}', copy: '检索游记、整理推荐理由并匹配地点信息…' },
      popular: { eyebrow: '快速开始', title: '热门目的地', copy: '选择一个城市，自动填入旅行主题' },
      create: { eyebrow: '新建行程', title: '先告诉我你的旅行想法', copy: '这些资料会用于检索真实游记并整理景点候选。', back: '返回探索', destination: '目的地城市', destinationPlaceholder: '例如：阿姆斯特丹、成都、京都', preference: '旅行偏好', preferencePlaceholder: '例如：历史文化、美食、亲子、摄影', source: '参考资料数量', language: '结果语言', submit: '生成景点灵感', steps: ['目的地', '旅行偏好', '景点候选'], pipelineTitle: '资料处理链', pipelineCopy: '每一步都对应真实服务，不生成虚构行程。', sourceStep: '小红书旅行笔记', llmStep: '提取景点候选', mapStep: '补充地图资料', saveStep: '保存到资料库' },
      library: { eyebrow: '我的资料', title: '已保存的探索记录', empty: '还没有保存记录', emptyCopy: '从目的地开始，生成第一份真实旅行资料。', start: '开始探索', latest: '最近一次探索', open: '查看记录' },
      result: {
        saved: '记录已保存', retry: '重新探索', notes: '{{count}} 篇游记', places: '{{count}} 个值得留意的地方', noPlaces: '没有找到合适的景点', noPlacesCopy: '换一个旅行偏好后重新试试。',
      },
      data: { source: '地图资料', weather: '出行天气', cached: '已缓存', loadingWeather: '正在查询天气', emptyWeather: '暂未获取到可用天气', hotel: '住宿候选', loadingHotel: '正在搜索住宿', emptyHotel: '暂未获取到住宿候选', addressPending: '地址待供应商补充', perNight: '/晚', reservation: '建议预约' },
      footer: { api: 'API 文档' },
      cities: { beijing: '北京', hangzhou: '杭州', chengdu: '成都', iceland: '冰岛', history: '历史文化', nature: '自然人文', food: '美食漫游', scenery: '自然风光' },
    },
  },
  en: {
    translation: {
      nav: { explore: 'Explore', library: 'My library', api: 'API', start: 'Plan a trip', homeAria: 'TravelMind AI home', mainAria: 'Main navigation' },
      status: { checking: 'Checking', offline: 'Disconnected', waiting: 'Needs setup', online: 'Online', refresh: 'Refresh service status' },
      hero: {
        kicker: 'AI TRAVEL PLANNER', title: 'Find the beauty in every journey', copy: 'Start every trip with real travel inspiration.',
        cityLabel: 'Destination', cityPlaceholder: 'Where do you want to go?', preferenceLabel: 'Travel style', preferencePlaceholder: 'Culture, food, family…',
        submit: 'Start planning', submitting: 'Preparing', notes: '{{count}} travel notes', noteAria: 'Reference travel notes', languageAria: 'Result language',
      },
      language: { zh: 'Chinese', en: 'English', ja: 'Japanese' },
      features: {
        aria: 'Travel planning capabilities', plan: 'AI planning', planSub: 'From ideas to routes', custom: 'Personalized', customSub: 'Built around you',
        trusted: 'Live information', trustedSub: 'Maps and weather', start: 'Ready to go', startSub: 'Save your discoveries',
      },
      error: { close: 'Dismiss', missingCity: 'Enter a destination first', enrichFailed: 'Places were saved, but weather and hotel data are unavailable for now', extractionFailed: 'Could not extract places. Please try again.' },
      loading: { title: 'Exploring {{city}}', copy: 'Reading travel notes, refining recommendations, and matching places…' },
      popular: { eyebrow: 'QUICK START', title: 'Popular destinations', copy: 'Pick a city to fill in a travel theme' },
      create: { eyebrow: 'NEW TRIP', title: 'Tell us about your trip', copy: 'We use these details to search real notes and organize place candidates.', back: 'Back to explore', destination: 'Destination city', destinationPlaceholder: 'e.g. Amsterdam, Chengdu, Kyoto', preference: 'Travel style', preferencePlaceholder: 'e.g. culture, food, family, photography', source: 'Reference notes', language: 'Result language', submit: 'Find place inspiration', steps: ['Destination', 'Travel style', 'Place candidates'], pipelineTitle: 'Data pipeline', pipelineCopy: 'Every step maps to a real service. No fabricated itinerary.', sourceStep: 'Xiaohongshu travel notes', llmStep: 'Extract place candidates', mapStep: 'Enrich map data', saveStep: 'Save to library' },
      library: { eyebrow: 'MY LIBRARY', title: 'Saved exploration records', empty: 'No saved records yet', emptyCopy: 'Start with a destination to create your first real travel brief.', start: 'Start exploring', latest: 'Latest exploration', open: 'View record' },
      result: { saved: 'Saved record', retry: 'Explore again', notes: '{{count}} travel notes', places: '{{count}} places to consider', noPlaces: 'No suitable places found', noPlacesCopy: 'Try a different travel style.' },
      data: { source: 'MAP DATA', weather: 'Travel weather', cached: 'Cached', loadingWeather: 'Checking weather', emptyWeather: 'No weather data available', hotel: 'Hotel options', loadingHotel: 'Searching hotels', emptyHotel: 'No hotel options available', addressPending: 'Address pending', perNight: '/ night', reservation: 'Reservation suggested' },
      footer: { api: 'API docs' },
      cities: { beijing: 'Beijing', hangzhou: 'Hangzhou', chengdu: 'Chengdu', iceland: 'Iceland', history: 'Culture & history', nature: 'Nature & culture', food: 'Food tour', scenery: 'Nature escape' },
    },
  },
  ja: {
    translation: {
      nav: { explore: '旅の発見', library: 'マイライブラリ', api: 'API', start: '旅を計画', homeAria: 'TravelMind AI ホーム', mainAria: 'メインナビゲーション' },
      status: { checking: '確認中', offline: '未接続', waiting: '設定待ち', online: '利用可能', refresh: 'サービス状態を更新' },
      hero: {
        kicker: 'AI 旅行プランナー', title: '世界の美しさを見つけよう', copy: '本物の旅のインスピレーションから旅を始めます。',
        cityLabel: '目的地', cityPlaceholder: 'どこへ行きますか？', preferenceLabel: '旅行の好み', preferencePlaceholder: '文化、グルメ、家族旅行…',
        submit: '計画を始める', submitting: '準備中', notes: '旅行記事 {{count}} 件', noteAria: '参照する旅行記事数', languageAria: '結果の言語',
      },
      language: { zh: '中国語', en: '英語', ja: '日本語' },
      features: { aria: '旅行計画機能', plan: 'AI プランニング', planSub: 'アイデアからルートまで', custom: 'パーソナル', customSub: '好みに合わせて', trusted: 'リアルタイム情報', trustedSub: '地図と天気', start: 'すぐ出発', startSub: '発見を保存' },
      error: { close: '閉じる', missingCity: '目的地を入力してください', enrichFailed: 'スポットは保存されましたが、天気とホテル情報を取得できません', extractionFailed: 'スポットを取得できませんでした。もう一度お試しください。' },
      loading: { title: '{{city}}を探索中', copy: '旅行記事を調べ、おすすめを整理し、場所情報を照合しています…' },
      popular: { eyebrow: 'クイックスタート', title: '人気の目的地', copy: '都市を選ぶと旅行テーマが入力されます' },
      create: { eyebrow: '新しい旅', title: '旅の希望を教えてください', copy: '実際の旅行記事を検索し、スポット候補を整理します。', back: '発見に戻る', destination: '目的地', destinationPlaceholder: '例：アムステルダム、成都、京都', preference: '旅行の好み', preferencePlaceholder: '例：文化、グルメ、家族旅行、写真', source: '参照する記事数', language: '結果の言語', submit: 'スポットを探す', steps: ['目的地', '旅行の好み', 'スポット候補'], pipelineTitle: 'データ処理', pipelineCopy: 'すべて実際のサービスに接続します。架空の旅程は作成しません。', sourceStep: '小紅書の旅行記事', llmStep: 'スポット候補を抽出', mapStep: '地図情報を補足', saveStep: 'ライブラリに保存' },
      library: { eyebrow: 'マイライブラリ', title: '保存した探索記録', empty: '保存された記録はありません', emptyCopy: '目的地から始めて、最初の旅行資料を作成しましょう。', start: '探索を始める', latest: '最近の探索', open: '記録を見る' },
      result: { saved: '保存済み', retry: 'もう一度探索', notes: '旅行記事 {{count}} 件', places: '注目のスポット {{count}} 件', noPlaces: 'スポットが見つかりません', noPlacesCopy: '旅行の好みを変えてお試しください。' },
      data: { source: '地図データ', weather: '旅行の天気', cached: 'キャッシュ済み', loadingWeather: '天気を検索中', emptyWeather: '利用できる天気情報がありません', hotel: 'ホテル候補', loadingHotel: 'ホテルを検索中', emptyHotel: '利用できるホテルがありません', addressPending: '住所情報待ち', perNight: '/泊', reservation: '予約をおすすめ' },
      footer: { api: 'API ドキュメント' },
      cities: { beijing: '北京', hangzhou: '杭州', chengdu: '成都', iceland: 'アイスランド', history: '歴史と文化', nature: '自然と人文', food: 'グルメ旅', scenery: '自然風景' },
    },
  },
} as const

const savedLanguage = typeof window === 'undefined' ? 'zh' : window.localStorage.getItem('travelmind-language')
const initialLanguage = savedLanguage === 'en' || savedLanguage === 'ja' ? savedLanguage : 'zh'

void i18n.use(initReactI18next).init({
  resources,
  lng: initialLanguage,
  fallbackLng: 'zh',
  interpolation: { escapeValue: false },
})

i18n.on('languageChanged', (language) => {
  if (typeof window !== 'undefined') window.localStorage.setItem('travelmind-language', language)
})

export default i18n

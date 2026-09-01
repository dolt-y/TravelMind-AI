import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const zh = {
  common: { language: '界面语言', hour: '小时', minute: '分钟', viewAll: '查看全部' },
  nav: { home: 'TravelMind AI 首页', main: '主导航', menu: '打开菜单', inspiration: '旅行灵感', plan: '开始规划', library: '我的资料', settings: '设置' },
  status: { checking: '检查服务', online: '服务可用', needs_config: '等待配置', offline: '服务未连接', refresh: '刷新服务状态' },
  footer: { copy: '从真实旅行资料开始规划', api: 'API 文档' },
  home: {
    eyebrow: '真实资料驱动的旅行规划', subtitle: '从旅行笔记里发现值得去的地方，再用地图、天气与住宿资料把灵感变成可执行的出发清单。', sourceNote: '小红书笔记检索 · LLM 景点提取 · 高德地点匹配', explore: '向下探索',
    popularEyebrow: '从一个地方开始', popularTitle: '近期旅行灵感', workflowEyebrow: '一次真实的数据处理', workflowTitle: '每个推荐都有资料来源', workflowCopy: '输入目的地后，系统检索旅行笔记、提取景点候选、补齐地图资料，并把结果保存到本地资料库。', workflowNotes: '检索旅行笔记', workflowExtract: '提取景点候选', workflowPoi: '匹配地点资料', workflowSave: '保存探索记录',
  },
  destinations: { amalfi: '阿马尔菲', kyoto: '京都', iceland: '冰岛', switzerland: '瑞士', coast: '海岸自驾', culture: '古都建筑', aurora: '极光自然', alpine: '湖泊徒步' },
  inspiration: { eyebrow: '旅行灵感', title: '从一种旅行感受开始', copy: '这些目的地只用于快速填写搜索条件，真正的景点内容来自你的实时查询。', use: '使用这个目的地' },
  planner: { destination: '目的地', destinationPlaceholder: '想去哪里？', preferences: '旅行偏好', preferencesPlaceholder: '美食、徒步、建筑、亲子…', noteCount: '参考笔记', notes: '{{count}} 篇', resultLanguage: '结果语言', submit: '开始规划' },
  plan: { eyebrow: '新建旅行资料', title: '说说你想去哪里', copy: '目的地是必填项，旅行偏好会帮助模型筛选更符合你的景点候选。', pipelineEyebrow: '数据去向', pipelineTitle: '不是一份临时结果', pipelineCopy: '原始笔记、结构化景点与地点资料会由后端保存；页面只持久化可继续查看的旅行结果。' },
  pipeline: { search: '搜索小红书旅行笔记', searchCopy: '读取与你的目的地和偏好相关的真实内容', extract: 'LLM 提取景点候选', extractCopy: '把自然语言笔记整理为可验证的结构化数据', poi: '高德 POI 匹配', poiCopy: '补充坐标、地址、评分和图片资料', persist: 'SQLite 持久化', persistCopy: '保存原始输入、提取结果与关联记录' },
  planning: { eyebrow: '正在处理旅行资料', title: '正在探索 {{city}}', copy: '这项任务包含外部内容检索与大模型处理，通常需要一些时间，请不要关闭页面。', failed: '本次规划没有完成', back: '返回修改条件' },
  results: { saved: '已保存的探索结果', title: '{{city}}旅行候选', summary: '参考 {{notes}} 篇旅行笔记，整理出 {{places}} 个地点', retry: '重新规划', placesEyebrow: '景点候选', places: '值得进一步了解的地方', favorite: '收藏地点', unfavorite: '取消收藏', reservation: '建议预约', addressPending: '地址待供应商补充', liveData: '实时供应商资料', weather: '出行天气', hotels: '住宿候选', weatherEmpty: '暂未获取到天气资料', hotelEmpty: '暂未获取到住宿资料', perNight: '/晚', noPlaces: '没有提取到合适的景点，请调整偏好后重试。', emptyTitle: '还没有旅行结果', emptyCopy: '先填写目的地并完成一次真实资料提取。', start: '开始规划' },
  library: { eyebrow: '我的资料', title: '继续上一次旅行探索', copy: '这里展示最近一次保存在浏览器中的结果索引，完整记录由后端数据库保存。', emptyTitle: '资料库还是空的', emptyCopy: '完成一次目的地探索后，结果会出现在这里。', start: '创建旅行资料', latest: '最近一次探索', summary: '{{notes}} 篇笔记 · {{places}} 个地点', noPreference: '未指定旅行偏好', open: '查看结果' },
  settings: { eyebrow: '设置', title: '服务与账户', copy: '管理界面语言、后端连接状态和小红书登录方式。', language: '界面语言', languageCopy: '切换导航、页面和操作文案', service: '后端服务', serviceCopy: '检查旅行资料服务是否可用', xhs: '小红书登录', xhsCopy: '通过二维码、手机号或 Cookie 建立登录态', manage: '管理登录', api: '开发接口', apiCopy: '查看当前 FastAPI 接口文档', openApi: '打开文档' },
  login: {
    eyebrow: '内容来源账户', title: '连接小红书', copy: '选择一种登录方式。登录凭证只提交给当前后端服务，前端不会持久化 Cookie。', method: '登录方式', qrcode: '二维码', phone: '手机号', qrAlt: '小红书登录二维码', qrReady: '生成二维码后使用小红书扫码', qrStart: '生成二维码', qrRestart: '重新生成', phoneNumber: '手机号码', code: '验证码', codePlaceholder: '输入短信验证码', sendCode: '发送验证码', verify: '验证并登录', cookieLabel: '真实 Cookie', cookieNote: 'Cookie 不会写入浏览器本地存储，提交成功后立即清空输入框。', cookieSubmit: '使用 Cookie 登录', error: '登录请求失败',
    states: { preparing: '正在准备', waiting_scan: '等待扫码', waiting_confirm: '等待手机确认', code_sent: '验证码已发送', authenticating: '正在验证', success: '登录成功', expired: '登录已过期', error: '登录失败' },
  },
  notFound: { copy: '没有找到这个页面。', home: '返回首页' },
}

const en = {
  common: { language: 'Interface language', hour: 'h', minute: 'min', viewAll: 'View all' },
  nav: { home: 'TravelMind AI home', main: 'Main navigation', menu: 'Open menu', inspiration: 'Inspiration', plan: 'Plan a trip', library: 'Library', settings: 'Settings' },
  status: { checking: 'Checking', online: 'Service online', needs_config: 'Setup required', offline: 'Disconnected', refresh: 'Refresh service status' },
  footer: { copy: 'Plan from real travel sources', api: 'API docs' },
  home: { eyebrow: 'TRAVEL PLANNING FROM REAL SOURCES', subtitle: 'Find places in travel notes, then turn inspiration into a practical shortlist with maps, weather, and accommodation data.', sourceNote: 'Xiaohongshu notes · LLM extraction · Amap POI matching', explore: 'Explore below', popularEyebrow: 'START WITH A PLACE', popularTitle: 'Travel ideas', workflowEyebrow: 'A REAL DATA PIPELINE', workflowTitle: 'Every suggestion starts with a source', workflowCopy: 'TravelMind searches notes, extracts place candidates, enriches map details, and saves the result to your library.', workflowNotes: 'Search travel notes', workflowExtract: 'Extract place candidates', workflowPoi: 'Match location data', workflowSave: 'Save the record' },
  destinations: { amalfi: 'Amalfi', kyoto: 'Kyoto', iceland: 'Iceland', switzerland: 'Switzerland', coast: 'Coastal road trip', culture: 'Historic architecture', aurora: 'Aurora & nature', alpine: 'Lakeside hiking' },
  inspiration: { eyebrow: 'INSPIRATION', title: 'Start with a feeling', copy: 'These destinations only prefill search criteria. Actual places come from your live query.', use: 'Use this destination' },
  planner: { destination: 'Destination', destinationPlaceholder: 'Where do you want to go?', preferences: 'Travel preferences', preferencesPlaceholder: 'Food, hiking, architecture, family…', noteCount: 'Reference notes', notes: '{{count}} notes', resultLanguage: 'Result language', submit: 'Start planning' },
  plan: { eyebrow: 'NEW TRAVEL BRIEF', title: 'Tell us where you want to go', copy: 'A destination is required. Preferences help the model select more relevant place candidates.', pipelineEyebrow: 'DATA DESTINATION', pipelineTitle: 'More than a temporary result', pipelineCopy: 'The backend stores source notes, structured places, and location data. The browser only keeps reusable trip results.' },
  pipeline: { search: 'Search Xiaohongshu notes', searchCopy: 'Read real content related to your destination', extract: 'Extract places with an LLM', extractCopy: 'Turn natural-language notes into structured data', poi: 'Match Amap POIs', poiCopy: 'Add coordinates, addresses, ratings, and photos', persist: 'Persist to SQLite', persistCopy: 'Save source inputs, extraction results, and links' },
  planning: { eyebrow: 'PROCESSING TRAVEL SOURCES', title: 'Exploring {{city}}', copy: 'This task includes external retrieval and model processing. It can take a moment; keep this page open.', failed: 'Planning could not be completed', back: 'Edit search criteria' },
  results: { saved: 'SAVED EXPLORATION', title: '{{city}} travel candidates', summary: '{{notes}} travel notes produced {{places}} places', retry: 'Plan again', placesEyebrow: 'PLACE CANDIDATES', places: 'Places worth a closer look', favorite: 'Save place', unfavorite: 'Remove from saved', reservation: 'Reservation suggested', addressPending: 'Address pending', liveData: 'LIVE PROVIDER DATA', weather: 'Travel weather', hotels: 'Accommodation', weatherEmpty: 'No weather data available', hotelEmpty: 'No hotel data available', perNight: '/night', noPlaces: 'No suitable places were extracted. Adjust your preferences and try again.', emptyTitle: 'No travel result yet', emptyCopy: 'Enter a destination and complete a real source extraction first.', start: 'Start planning' },
  library: { eyebrow: 'MY LIBRARY', title: 'Continue your latest exploration', copy: 'This page shows the latest result index kept in this browser. Full records live in the backend database.', emptyTitle: 'Your library is empty', emptyCopy: 'Complete a destination search and the result will appear here.', start: 'Create a travel brief', latest: 'Latest exploration', summary: '{{notes}} notes · {{places}} places', noPreference: 'No preference specified', open: 'View result' },
  settings: { eyebrow: 'SETTINGS', title: 'Services and accounts', copy: 'Manage interface language, backend status, and Xiaohongshu authentication.', language: 'Interface language', languageCopy: 'Change navigation and page copy', service: 'Backend service', serviceCopy: 'Check whether travel data services are available', xhs: 'Xiaohongshu login', xhsCopy: 'Connect with QR code, phone, or Cookie', manage: 'Manage login', api: 'Developer API', apiCopy: 'Open the current FastAPI documentation', openApi: 'Open docs' },
  login: { eyebrow: 'CONTENT SOURCE ACCOUNT', title: 'Connect Xiaohongshu', copy: 'Choose a login method. Credentials are sent only to the current backend and Cookies are never persisted by the frontend.', method: 'Login method', qrcode: 'QR code', phone: 'Phone', qrAlt: 'Xiaohongshu login QR code', qrReady: 'Generate a code and scan it with Xiaohongshu', qrStart: 'Generate code', qrRestart: 'Generate again', phoneNumber: 'Phone number', code: 'Verification code', codePlaceholder: 'Enter SMS code', sendCode: 'Send code', verify: 'Verify and log in', cookieLabel: 'Real Cookie', cookieNote: 'The Cookie is not written to browser storage and the input is cleared after submission.', cookieSubmit: 'Log in with Cookie', error: 'Login request failed', states: { preparing: 'Preparing', waiting_scan: 'Waiting for scan', waiting_confirm: 'Waiting for confirmation', code_sent: 'Code sent', authenticating: 'Authenticating', success: 'Signed in', expired: 'Login expired', error: 'Login failed' } },
  notFound: { copy: 'This page could not be found.', home: 'Back home' },
}

const ja = {
  common: { language: '表示言語', hour: '時間', minute: '分', viewAll: 'すべて見る' },
  nav: { home: 'TravelMind AI ホーム', main: 'メインナビゲーション', menu: 'メニューを開く', inspiration: '旅の発見', plan: '旅を計画', library: 'ライブラリ', settings: '設定' },
  status: { checking: '確認中', online: 'サービス利用可能', needs_config: '設定が必要', offline: '未接続', refresh: 'サービス状態を更新' },
  footer: { copy: '実際の旅行資料から計画', api: 'API ドキュメント' },
  home: { eyebrow: '実際の資料に基づく旅行計画', subtitle: '旅行記事から場所を見つけ、地図・天気・宿泊情報で実行できる候補に整理します。', sourceNote: '小紅書の記事 · LLM 抽出 · 高徳地図 POI', explore: '下へ見る', popularEyebrow: '場所から始める', popularTitle: '旅のアイデア', workflowEyebrow: '実際のデータ処理', workflowTitle: 'すべての候補に情報源があります', workflowCopy: '記事を検索し、場所を抽出し、地図情報を補足してライブラリに保存します。', workflowNotes: '旅行記事を検索', workflowExtract: '場所候補を抽出', workflowPoi: '地点情報を照合', workflowSave: '記録を保存' },
  destinations: { amalfi: 'アマルフィ', kyoto: '京都', iceland: 'アイスランド', switzerland: 'スイス', coast: '海岸ドライブ', culture: '古都の建築', aurora: 'オーロラと自然', alpine: '湖畔ハイキング' },
  inspiration: { eyebrow: '旅の発見', title: '旅の気分から始めよう', copy: '目的地は検索条件の入力用です。実際の場所はリアルタイム検索から取得します。', use: 'この目的地を使う' },
  planner: { destination: '目的地', destinationPlaceholder: 'どこへ行きますか？', preferences: '旅行の好み', preferencesPlaceholder: 'グルメ、ハイキング、建築、家族…', noteCount: '参照記事', notes: '{{count}} 件', resultLanguage: '結果の言語', submit: '計画を始める' },
  plan: { eyebrow: '新しい旅行資料', title: '行きたい場所を教えてください', copy: '目的地は必須です。好みに合わせて場所候補を選びます。', pipelineEyebrow: 'データの保存先', pipelineTitle: '一時的な結果ではありません', pipelineCopy: '元の記事、構造化された場所、地図情報はバックエンドに保存されます。' },
  pipeline: { search: '小紅書の旅行記事を検索', searchCopy: '目的地に関連する実際の記事を読み取ります', extract: 'LLM で場所候補を抽出', extractCopy: '自然言語を構造化データに整理します', poi: '高徳地図 POI を照合', poiCopy: '座標、住所、評価、写真を補足します', persist: 'SQLite に保存', persistCopy: '入力、抽出結果、関連情報を保存します' },
  planning: { eyebrow: '旅行資料を処理中', title: '{{city}}を探索中', copy: '外部検索とモデル処理を行うため、しばらくお待ちください。このページを閉じないでください。', failed: '計画を完了できませんでした', back: '条件を変更する' },
  results: { saved: '保存済みの探索結果', title: '{{city}}の旅行候補', summary: '{{notes}} 件の記事から {{places}} 地点を整理しました', retry: 'もう一度計画', placesEyebrow: '場所候補', places: '詳しく調べたい場所', favorite: '保存', unfavorite: '保存を解除', reservation: '予約推奨', addressPending: '住所情報待ち', liveData: 'リアルタイム資料', weather: '旅行の天気', hotels: '宿泊候補', weatherEmpty: '天気情報がありません', hotelEmpty: '宿泊情報がありません', perNight: '/泊', noPlaces: '場所が見つかりません。好みを変更して再試行してください。', emptyTitle: '旅行結果がありません', emptyCopy: '目的地を入力して資料の抽出を完了してください。', start: '計画を始める' },
  library: { eyebrow: 'ライブラリ', title: '前回の探索を続ける', copy: 'ブラウザに保存された最新結果を表示します。完全な記録はバックエンドに保存されます。', emptyTitle: 'ライブラリは空です', emptyCopy: '目的地を探索すると結果がここに表示されます。', start: '旅行資料を作る', latest: '最近の探索', summary: '{{notes}} 件の記事 · {{places}} 地点', noPreference: '好みの指定なし', open: '結果を見る' },
  settings: { eyebrow: '設定', title: 'サービスとアカウント', copy: '表示言語、バックエンド、小紅書ログインを管理します。', language: '表示言語', languageCopy: 'ナビゲーションとページの言語を変更', service: 'バックエンド', serviceCopy: '旅行データサービスの状態を確認', xhs: '小紅書ログイン', xhsCopy: 'QR、電話番号、Cookie で接続', manage: 'ログイン管理', api: '開発 API', apiCopy: 'FastAPI ドキュメントを表示', openApi: 'ドキュメント' },
  login: { eyebrow: 'コンテンツアカウント', title: '小紅書に接続', copy: 'ログイン方法を選択してください。Cookie はフロントエンドに保存されません。', method: 'ログイン方法', qrcode: 'QR コード', phone: '電話番号', qrAlt: '小紅書ログイン QR コード', qrReady: 'QR コードを生成して小紅書でスキャン', qrStart: 'QR を生成', qrRestart: '再生成', phoneNumber: '電話番号', code: '確認コード', codePlaceholder: 'SMS コードを入力', sendCode: 'コードを送信', verify: '確認してログイン', cookieLabel: '実際の Cookie', cookieNote: 'Cookie はブラウザに保存されず、送信後に入力欄を消去します。', cookieSubmit: 'Cookie でログイン', error: 'ログインに失敗しました', states: { preparing: '準備中', waiting_scan: 'スキャン待ち', waiting_confirm: '確認待ち', code_sent: 'コード送信済み', authenticating: '確認中', success: 'ログイン成功', expired: '期限切れ', error: 'ログイン失敗' } },
  notFound: { copy: 'ページが見つかりません。', home: 'ホームへ戻る' },
}

const savedLanguage = typeof window === 'undefined' ? 'zh' : window.localStorage.getItem('travelmind-language')
const initialLanguage = savedLanguage === 'en' || savedLanguage === 'ja' ? savedLanguage : 'zh'

void i18n.use(initReactI18next).init({
  resources: { zh: { translation: zh }, en: { translation: en }, ja: { translation: ja } },
  lng: initialLanguage,
  fallbackLng: 'zh',
  interpolation: { escapeValue: false },
})

i18n.on('languageChanged', (language) => {
  if (typeof window !== 'undefined') window.localStorage.setItem('travelmind-language', language)
})

export default i18n

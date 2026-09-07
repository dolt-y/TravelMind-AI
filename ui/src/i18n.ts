import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const zh = {
  common: { language: '界面语言', hour: '小时', minute: '分钟', viewAll: '查看全部' },
  nav: { home: 'TravelMind 首页', homeLink: '首页', main: '主导航', menu: '打开菜单', inspiration: '灵感探索', plan: '规划行程', library: '我的资料', settings: '账户设置' },
  footer: { copy: '让每一次旅行更有意义' },
  home: {
    title: '探索世界，\n遇见更好的自己', subtitle: 'AI 智能规划专属行程，让每一次旅行更有意义', search: '开始规划', hotSearch: '热门目的地：',
    popularEyebrow: 'POPULAR DESTINATIONS', popularTitle: '热门目的地',
    flowEyebrow: 'HOW IT WORKS', flowTitle: '从旅行灵感到安心出发', flowCopy: '从真实旅行笔记中发现值得去的地方，再逐步补全信息并编排属于你的行程。', flowSource: '旅行灵感来自小红书',
    flowSteps: { needs: '描述旅行需求', needsCopy: '填写目的地、旅行偏好、时间与预算', inspiration: '检索旅行笔记', inspirationCopy: '从小红书真实分享中寻找旅行灵感', places: '整理景点候选', placesCopy: '从旅行笔记中筛选更符合偏好的地点', details: '补充出行信息', detailsCopy: '完善位置、天气、住宿与注意事项', itinerary: '编排行程路线', itineraryCopy: '平衡游玩顺序、节奏与交通距离', refine: '收藏持续调整', refineCopy: '保留喜欢的地点，随时完善旅程' },
  },
  destinations: { amalfi: '阿马尔菲海岸', kyoto: '日本京都', iceland: '冰岛极光之旅', switzerland: '瑞士因特拉肯', norway: '挪威峡湾', coast: '意大利', culture: '日本', aurora: '冰岛', alpine: '瑞士', hiking: '海岸徒步' },
  inspiration: { eyebrow: '旅行灵感', title: '从一种旅行感受开始', copy: '这些目的地只用于快速填写搜索条件，真正的景点内容来自你的实时查询。', use: '使用这个目的地' },
  planner: { destination: '目的地', destinationPlaceholder: '想去哪里？', preferences: '旅行偏好', preferencesPlaceholder: '美食、徒步、建筑、亲子…', startDate: '出发日期', endDate: '返回日期', transportation: '市内交通', travelers: '出行人数', accommodation: '住宿偏好', hotelBudget: '每晚住宿预算', totalBudget: '整段行程预算', noteCount: '参考笔记', notes: '{{count}} 篇', resultLanguage: '结果语言', transport: { walking: '步行优先', transit: '公共交通', driving: '自驾' }, stays: { budget: '经济型酒店', comfort: '舒适型酒店', premium: '高档酒店', local: '特色民宿' }, submit: '开始规划' },
  plan: { eyebrow: '规划新的旅程', title: '说说你的出行安排', copy: '补充日期、同行人数和旅行偏好，我们会生成一份可以按天执行的行程。', pipelineEyebrow: '规划过程', pipelineTitle: '从灵感到每日行程', pipelineCopy: '真实旅行分享提供灵感，天气、住宿和路线帮助行程更贴近实际。' },
  pipeline: { search: '寻找旅行灵感', searchCopy: '从真实旅行分享中整理推荐地点', extract: '整理推荐地点', extractCopy: '从旅行分享中找到更符合你偏好的选择', poi: '确认地点信息', poiCopy: '补充地址、位置、评分和图片', context: '了解出行条件', contextCopy: '查询天气和合适的住宿选择', itinerary: '编排每日行程', itineraryCopy: '结合日期、偏好和游玩节奏安排景点', routes: '计算相邻路线', routesCopy: '确认每天各地点之间的距离和时间', finalize: '完成行程核对' },
  planning: { eyebrow: '正在规划专属行程', title: '正在规划 {{city}}', copy: '正在逐步整理地点、住宿和路线，这通常需要几分钟。', progress: '当前进度 {{progress}}%', failed: '本次规划没有完成', back: '返回修改条件' },
  results: { saved: '完整旅行计划', title: '{{city}}行程', summary: '{{start}} 至 {{end}} · 共 {{days}} 天', retry: '重新规划', itineraryEyebrow: '每日安排', itinerary: '你的逐日行程', day: '第 {{day}} 天', transferDay: '城市移动日', routes: '地点间路线', meals: '用餐建议', stay: '当晚住宿', mealTypes: { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }, favorite: '收藏地点', unfavorite: '取消收藏', reservation: '建议预约', addressPending: '地点地址暂未完善', travelReference: '出行参考', weather: '行程天气', hotels: '住宿选择', weatherEmpty: '当前日期暂无可用天气预报', hotelEmpty: '暂时没有合适的住宿信息', perNight: '/晚', knownBudget: '当前已知费用估算', emptyTitle: '还没有旅行结果', emptyCopy: '先填写出行需求，生成你的第一份完整行程。', start: '开始规划' },
  tripVisuals: {
    eyebrow: '行程概览',
    map: { title: '每日行程地图', days: '选择查看日期', day: '第 {{day}} 天', loading: '正在绘制当天路线', unavailable: '地图暂时无法显示，请稍后再试', empty: '当天暂无可展示的位置与路线', error: '地图加载失败，请稍后重试', aria: '第 {{day}} 天 {{city}} 行程地图' },
    budget: { title: '费用构成', total: '当前合计', empty: '暂无可展示的费用估算', aria: '行程费用构成，当前合计 {{total}}', categories: { attractions: '景点', hotels: '住宿', meals: '餐饮', transportation: '交通' } },
  },
  library: { eyebrow: '我的行程', title: '你的旅行计划', copy: '查看已经生成的完整旅行安排。', emptyTitle: '这里还是空的', emptyCopy: '完成一次旅行规划后，行程会出现在这里。', start: '开始规划' },
  libraryHistory: { count: '共 {{count}} 个行程', loading: '正在读取你的行程', loadFailed: '暂时无法读取行程，请稍后重试。', retry: '重新加载', days: '{{count}} 天', travelers: '{{count}} 人', created: '{{date}} 创建', openNamed: '查看 {{city}} 行程', openFailed: '暂时无法打开这个行程，请重新尝试。' },
  settings: { eyebrow: '账户设置', title: '偏好与账户', copy: '管理你的使用偏好。', language: '界面语言', languageCopy: '切换导航、页面和操作文案' },
  adminXhs: {
    shell: { label: '内部管理', back: '返回用户端', exit: '退出管理' },
    eyebrow: '系统内容来源', title: '小红书内容账号管理', copy: '维护 TravelMind 获取旅行灵感所使用的系统账号。此页面仅面向授权管理员。',
    authRequired: '当前内容账号需要重新登录。管理员完成登录后，可返回继续本次旅行规划。',
    context: { eyebrow: 'TRAVELMIND CONTENT', title: '让真实旅行分享持续可用', copy: '系统账号只负责获取旅行灵感，普通用户无需接触任何登录信息。', security: '仅授权管理员可以维护账号', source: '为目的地规划提供真实旅行分享', return: '更新完成后继续原来的旅行规划' },
    access: { title: '验证管理员身份', copy: '输入服务端配置的管理密钥后才能维护系统账号。', keyLabel: '管理密钥', keyPlaceholder: '输入内部管理密钥', showKey: '显示密钥', hideKey: '隐藏密钥', memoryOnly: '密钥仅保留在当前页面内存中，刷新或退出后自动清除。', submit: '进入管理', verified: '管理员已验证' },
    account: { eyebrow: '账号维护', title: '小红书系统账号', copy: '选择一种方式更新当前服务使用的内容账号会话。普通用户不会看到或接触这些登录信息。' },
    login: { method: '登录方式', qrcode: '二维码', phone: '手机号', qrAlt: '小红书系统账号登录二维码', qrReady: '生成二维码后使用小红书扫码', qrStart: '生成二维码', qrRestart: '重新生成', zone: '区号', phoneNumber: '手机号码', code: '验证码', codePlaceholder: '输入短信验证码', sendCode: '发送验证码', verify: '验证并登录', cookieLabel: 'Cookie', cookieNote: 'Cookie 只会提交给当前 TravelMind 服务，不会保存在浏览器中。', cookieSubmit: '验证 Cookie', currentUser: '当前账号：{{name}}', continuePlanning: '返回并重新规划' },
    states: { preparing: '正在准备', waiting_scan: '等待扫码', waiting_confirm: '等待手机确认', code_sent: '验证码已发送', authenticating: '正在验证', success: '系统账号已更新', expired: '登录已过期', error: '登录失败' },
    logout: { title: '清除登录态', copy: '清除后，旅行内容检索将暂停，直到管理员重新登录。', action: '清除登录态', confirm: '确定清除当前小红书系统账号的登录态吗？', success: '小红书登录态已清除' },
    errors: { access: '管理员验证失败', request: '账号维护请求失败', qrcode: '二维码加载失败，请重新生成', logout: '登录态清理失败，请重试。' },
  },
  notFound: { copy: '没有找到这个页面。', home: '返回首页' },
}

const en = {
  common: { language: 'Interface language', hour: 'h', minute: 'min', viewAll: 'View all' },
  nav: { home: 'TravelMind home', homeLink: 'Home', main: 'Main navigation', menu: 'Open menu', inspiration: 'Explore', plan: 'Plan a trip', library: 'My trips', settings: 'Account' },
  footer: { copy: 'Make every journey more meaningful' },
  home: {
    title: 'Explore the world.\nMeet a better you.', subtitle: 'Personalized AI trip planning to make every journey more meaningful', search: 'Start planning', hotSearch: 'Popular:',
    popularEyebrow: 'POPULAR DESTINATIONS', popularTitle: 'Popular destinations',
    flowEyebrow: 'HOW IT WORKS', flowTitle: 'From inspiration to departure', flowCopy: 'Discover places through real travel notes, complete the practical details, and shape your itinerary.', flowSource: 'Travel inspiration from Xiaohongshu',
    flowSteps: { needs: 'Share your needs', needsCopy: 'Add your destination, interests, time, and budget', inspiration: 'Search travel notes', inspirationCopy: 'Find inspiration in real Xiaohongshu stories', places: 'Organize place ideas', placesCopy: 'Shortlist places that fit your preferences', details: 'Complete trip details', detailsCopy: 'Review locations, weather, stays, and practical tips', itinerary: 'Shape the itinerary', itineraryCopy: 'Balance route order, pace, and travel distance', refine: 'Save and refine', refineCopy: 'Keep favorite places and adjust anytime' },
  },
  destinations: { amalfi: 'Amalfi Coast', kyoto: 'Kyoto, Japan', iceland: 'Iceland Aurora', switzerland: 'Interlaken', norway: 'Norwegian Fjords', coast: 'Italy', culture: 'Japan', aurora: 'Iceland', alpine: 'Switzerland', hiking: 'Coastal hiking' },
  inspiration: { eyebrow: 'INSPIRATION', title: 'Start with a feeling', copy: 'These destinations only prefill search criteria. Actual places come from your live query.', use: 'Use this destination' },
  planner: { destination: 'Destination', destinationPlaceholder: 'Where do you want to go?', preferences: 'Travel preferences', preferencesPlaceholder: 'Food, hiking, architecture, family…', startDate: 'Departure', endDate: 'Return', transportation: 'Local transport', travelers: 'Travelers', accommodation: 'Stay preference', hotelBudget: 'Nightly stay budget', totalBudget: 'Total trip budget', noteCount: 'Reference notes', notes: '{{count}} notes', resultLanguage: 'Result language', transport: { walking: 'Walk first', transit: 'Public transit', driving: 'Drive' }, stays: { budget: 'Budget hotel', comfort: 'Comfort hotel', premium: 'Premium hotel', local: 'Local stay' }, submit: 'Start planning' },
  plan: { eyebrow: 'PLAN A NEW JOURNEY', title: 'Share your travel details', copy: 'Add dates, travelers, and interests to create a practical day-by-day itinerary.', pipelineEyebrow: 'HOW IT WORKS', pipelineTitle: 'From inspiration to itinerary', pipelineCopy: 'Real travel stories provide ideas, while weather, stays, and routes keep the plan practical.' },
  pipeline: { search: 'Find travel inspiration', searchCopy: 'Shortlist places from real travel stories', extract: 'Organize recommended places', extractCopy: 'Find options that better match your travel style', poi: 'Confirm place details', poiCopy: 'Add addresses, locations, ratings, and photos', context: 'Review travel conditions', contextCopy: 'Check weather and suitable places to stay', itinerary: 'Build the daily itinerary', itineraryCopy: 'Balance dates, interests, and pace', routes: 'Calculate local routes', routesCopy: 'Confirm distance and time between daily stops', finalize: 'Review the complete plan' },
  planning: { eyebrow: 'BUILDING YOUR ITINERARY', title: 'Planning {{city}}', copy: 'We are organizing places, stays, and routes. This usually takes a few minutes.', progress: '{{progress}}% complete', failed: 'Planning could not be completed', back: 'Edit preferences' },
  results: { saved: 'COMPLETE TRIP PLAN', title: '{{city}} itinerary', summary: '{{start}} to {{end}} · {{days}} days', retry: 'Plan again', itineraryEyebrow: 'DAY BY DAY', itinerary: 'Your daily itinerary', day: 'Day {{day}}', transferDay: 'Transfer day', routes: 'Routes between stops', meals: 'Meal ideas', stay: 'Tonight’s stay', mealTypes: { breakfast: 'Breakfast', lunch: 'Lunch', dinner: 'Dinner', snack: 'Snack' }, favorite: 'Favorite place', unfavorite: 'Remove favorite', reservation: 'Reservation suggested', addressPending: 'Address not available yet', travelReference: 'TRAVEL REFERENCE', weather: 'Trip weather', hotels: 'Places to stay', weatherEmpty: 'No forecast is available for these dates yet', hotelEmpty: 'No suitable stay is available yet', perNight: '/night', knownBudget: 'Known cost estimate', emptyTitle: 'No trip plan yet', emptyCopy: 'Add your travel details to create your first complete itinerary.', start: 'Start planning' },
  tripVisuals: {
    eyebrow: 'TRIP OVERVIEW',
    map: { title: 'Daily route map', days: 'Choose a day to view', day: 'Day {{day}}', loading: 'Drawing the day route', unavailable: 'The map is temporarily unavailable. Please try again later.', empty: 'No locations or routes are available for this day', error: 'The map could not be loaded. Please try again later.', aria: 'Day {{day}} itinerary map for {{city}}' },
    budget: { title: 'Cost breakdown', total: 'Current total', empty: 'No cost estimate is available yet', aria: 'Trip cost breakdown, current total {{total}}', categories: { attractions: 'Attractions', hotels: 'Stays', meals: 'Meals', transportation: 'Transport' } },
  },
  library: { eyebrow: 'MY TRIPS', title: 'Your trip plans', copy: 'Review your completed travel itineraries.', emptyTitle: 'Nothing here yet', emptyCopy: 'Complete a trip plan and it will appear here.', start: 'Plan a trip' },
  libraryHistory: { count: '{{count}} trips', loading: 'Loading your trips', loadFailed: 'Your trips could not be loaded. Please try again.', retry: 'Reload', days: '{{count}} days', travelers: '{{count}} travelers', created: 'Created {{date}}', openNamed: 'View {{city}} trip', openFailed: 'This trip could not be opened. Please try again.' },
  settings: { eyebrow: 'ACCOUNT', title: 'Preferences and account', copy: 'Manage your experience preferences.', language: 'Interface language', languageCopy: 'Change navigation and page copy' },
  adminXhs: {
    shell: { label: 'Internal admin', back: 'Back to site', exit: 'Exit admin' },
    eyebrow: 'SYSTEM CONTENT SOURCE', title: 'Xiaohongshu content account', copy: 'Maintain the system account TravelMind uses to find travel inspiration. This page is for authorized administrators only.',
    authRequired: 'The content account needs to be signed in again. Once updated, return to retry this trip plan.',
    context: { eyebrow: 'TRAVELMIND CONTENT', title: 'Keep real travel stories available', copy: 'The system account is used only to find travel inspiration. Regular users never handle its sign-in details.', security: 'Restricted to authorized administrators', source: 'Supports destination planning with real travel stories', return: 'Continue the original trip plan after updating' },
    access: { title: 'Verify administrator access', copy: 'Enter the management key configured on the server before maintaining the system account.', keyLabel: 'Management key', keyPlaceholder: 'Enter internal management key', showKey: 'Show key', hideKey: 'Hide key', memoryOnly: 'The key stays only in this page memory and is cleared on refresh or exit.', submit: 'Enter administration', verified: 'Administrator verified' },
    account: { eyebrow: 'ACCOUNT MAINTENANCE', title: 'Xiaohongshu system account', copy: 'Choose a method to update the content account session used by this service. Regular users never see or handle these credentials.' },
    login: { method: 'Login method', qrcode: 'QR code', phone: 'Phone', qrAlt: 'Xiaohongshu system account login QR code', qrReady: 'Generate a code and scan it with Xiaohongshu', qrStart: 'Generate QR code', qrRestart: 'Generate again', zone: 'Code', phoneNumber: 'Phone number', code: 'Verification code', codePlaceholder: 'Enter SMS code', sendCode: 'Send code', verify: 'Verify and log in', cookieLabel: 'Cookie', cookieNote: 'The Cookie is submitted only to this TravelMind service and is not stored in the browser.', cookieSubmit: 'Verify Cookie', currentUser: 'Current account: {{name}}', continuePlanning: 'Return and retry plan' },
    states: { preparing: 'Preparing', waiting_scan: 'Waiting for scan', waiting_confirm: 'Waiting for phone confirmation', code_sent: 'Code sent', authenticating: 'Authenticating', success: 'System account updated', expired: 'Login expired', error: 'Login failed' },
    logout: { title: 'Clear session', copy: 'Travel-content retrieval will pause until an administrator signs in again.', action: 'Clear session', confirm: 'Clear the current Xiaohongshu system-account session?', success: 'Xiaohongshu session cleared' },
    errors: { access: 'Administrator verification failed', request: 'Account maintenance request failed', qrcode: 'Could not load the QR code. Generate a new one.', logout: 'The session could not be cleared. Try again.' },
  },
  notFound: { copy: 'This page could not be found.', home: 'Back home' },
}

const ja = {
  common: { language: '表示言語', hour: '時間', minute: '分', viewAll: 'すべて見る' },
  nav: { home: 'TravelMind ホーム', homeLink: 'ホーム', main: 'メインナビゲーション', menu: 'メニューを開く', inspiration: '旅の発見', plan: '旅を計画', library: 'マイトリップ', settings: 'アカウント' },
  footer: { copy: 'すべての旅をもっと意味のあるものに' },
  home: {
    title: '世界を旅して、\n新しい自分に出会う', subtitle: 'AI があなたらしい旅を計画し、すべての旅をもっと意味のあるものに', search: '計画を始める', hotSearch: '人気の目的地：',
    popularEyebrow: 'POPULAR DESTINATIONS', popularTitle: '人気の目的地',
    flowEyebrow: 'HOW IT WORKS', flowTitle: '旅の発見から出発まで', flowCopy: 'リアルな旅行記事から場所を見つけ、必要な情報を整えて旅程を組み立てます。', flowSource: '旅の発見は小紅書から',
    flowSteps: { needs: '旅の希望を伝える', needsCopy: '目的地、興味、時間、予算を入力', inspiration: '旅行記事を探す', inspirationCopy: '小紅書のリアルな投稿から発見', places: '候補地を整理', placesCopy: '好みに合う観光地や体験を選ぶ', details: '旅の情報を整える', detailsCopy: '位置、天気、宿泊、注意点を確認', itinerary: '旅程を組み立てる', itineraryCopy: '順序、ペース、移動距離を調整', refine: '保存して調整', refineCopy: '好きな場所を残し、いつでも見直す' },
  },
  destinations: { amalfi: 'アマルフィ海岸', kyoto: '日本・京都', iceland: 'アイスランドのオーロラ', switzerland: 'インターラーケン', norway: 'ノルウェーのフィヨルド', coast: 'イタリア', culture: '日本', aurora: 'アイスランド', alpine: 'スイス', hiking: '海岸ハイキング' },
  inspiration: { eyebrow: '旅の発見', title: '旅の気分から始めよう', copy: '目的地は検索条件の入力用です。実際の場所はリアルタイム検索から取得します。', use: 'この目的地を使う' },
  planner: { destination: '目的地', destinationPlaceholder: 'どこへ行きますか？', preferences: '旅行の好み', preferencesPlaceholder: 'グルメ、ハイキング、建築、家族…', startDate: '出発日', endDate: '帰着日', transportation: '現地の移動', travelers: '人数', accommodation: '宿泊の好み', hotelBudget: '1泊の予算', totalBudget: '旅行全体の予算', noteCount: '参照記事', notes: '{{count}} 件', resultLanguage: '結果の言語', transport: { walking: '徒歩中心', transit: '公共交通', driving: '車' }, stays: { budget: 'リーズナブル', comfort: '快適なホテル', premium: '上質なホテル', local: '個性的な宿' }, submit: '計画を始める' },
  plan: { eyebrow: '新しい旅を計画', title: '旅行の予定を教えてください', copy: '日付、人数、好みを入力すると、実行しやすい日別プランを作成します。', pipelineEyebrow: '旅ができるまで', pipelineTitle: '発見から日別プランへ', pipelineCopy: 'リアルな旅行記事を起点に、天気、宿泊、ルートを組み合わせて計画します。' },
  pipeline: { search: '旅のヒントを探す', searchCopy: 'リアルな旅行記事から候補地を整理', extract: 'おすすめ場所を整理', extractCopy: '旅行の好みに合う場所を選びます', poi: '場所の情報を確認', poiCopy: '住所、位置、評価、写真を補足します', context: '旅行条件を確認', contextCopy: '天気と宿泊候補を確認します', itinerary: '日別プランを作成', itineraryCopy: '日付、好み、ペースを考えて配置', routes: '移動ルートを計算', routesCopy: '各日の場所間の距離と時間を確認', finalize: '旅程全体を確認' },
  planning: { eyebrow: '旅程を作成中', title: '{{city}}を計画中', copy: '場所、宿泊、ルートを整理しています。数分かかる場合があります。', progress: '進捗 {{progress}}%', failed: '計画を完了できませんでした', back: '条件を変更する' },
  results: { saved: '旅行プラン', title: '{{city}}の旅程', summary: '{{start}} から {{end}} · {{days}} 日間', retry: 'もう一度計画', itineraryEyebrow: '日別スケジュール', itinerary: 'あなたの旅程', day: '{{day}} 日目', transferDay: '都市移動日', routes: '場所間のルート', meals: '食事の提案', stay: '今夜の宿泊', mealTypes: { breakfast: '朝食', lunch: '昼食', dinner: '夕食', snack: '軽食' }, favorite: 'お気に入り', unfavorite: 'お気に入りを解除', reservation: '予約推奨', addressPending: '住所は準備中です', travelReference: '旅の参考', weather: '旅程の天気', hotels: '宿泊候補', weatherEmpty: 'この日程の天気予報はまだありません', hotelEmpty: '宿泊情報はまだありません', perNight: '/泊', knownBudget: '確認できた費用の目安', emptyTitle: '旅程がありません', emptyCopy: '旅行条件を入力して最初の旅程を作りましょう。', start: '計画を始める' },
  tripVisuals: {
    eyebrow: '旅程の概要',
    map: { title: '日別ルートマップ', days: '表示する日を選択', day: '{{day}} 日目', loading: '当日のルートを描画中', unavailable: '地図を一時的に表示できません。しばらくしてからお試しください。', empty: 'この日に表示できる場所やルートはありません', error: '地図を読み込めませんでした。しばらくしてからお試しください。', aria: '{{day}} 日目 {{city}} の旅程マップ' },
    budget: { title: '費用の内訳', total: '現在の合計', empty: '表示できる費用の目安はまだありません', aria: '旅行費用の内訳、現在の合計 {{total}}', categories: { attractions: '観光', hotels: '宿泊', meals: '食事', transportation: '交通' } },
  },
  library: { eyebrow: 'マイトリップ', title: 'あなたの旅行プラン', copy: '作成済みの旅程を確認できます。', emptyTitle: 'まだ何もありません', emptyCopy: '旅行を計画すると旅程がここに表示されます。', start: '旅を計画' },
  libraryHistory: { count: '{{count}} 件の旅程', loading: '旅程を読み込み中', loadFailed: '旅程を読み込めませんでした。しばらくしてからお試しください。', retry: '再読み込み', days: '{{count}} 日間', travelers: '{{count}} 人', created: '{{date}} に作成', openNamed: '{{city}} の旅程を見る', openFailed: 'この旅程を開けませんでした。もう一度お試しください。' },
  settings: { eyebrow: 'アカウント', title: '好みとアカウント', copy: '利用時の好みを管理します。', language: '表示言語', languageCopy: 'ナビゲーションとページの言語を変更' },
  adminXhs: {
    shell: { label: '内部管理', back: 'ユーザー画面へ', exit: '管理を終了' },
    eyebrow: 'システムコンテンツソース', title: '小紅書コンテンツアカウント管理', copy: 'TravelMind が旅行情報を探すために使用するシステムアカウントを管理します。このページは管理者専用です。',
    authRequired: 'コンテンツアカウントへの再ログインが必要です。更新後、この旅行プランをもう一度実行できます。',
    context: { eyebrow: 'TRAVELMIND CONTENT', title: 'リアルな旅行情報をいつでも利用可能に', copy: 'システムアカウントは旅行のヒントを探すためだけに使われ、一般ユーザーがログイン情報を扱うことはありません。', security: '認証済み管理者のみ管理できます', source: 'リアルな旅行投稿を目的地計画に活用', return: '更新後は元の旅行計画を続行できます' },
    access: { title: '管理者認証', copy: 'システムアカウントを管理するには、サーバーに設定された管理キーを入力してください。', keyLabel: '管理キー', keyPlaceholder: '内部管理キーを入力', showKey: 'キーを表示', hideKey: 'キーを隠す', memoryOnly: 'キーはこのページのメモリにのみ保持され、再読み込みまたは終了時に消去されます。', submit: '管理画面へ', verified: '管理者認証済み' },
    account: { eyebrow: 'アカウント管理', title: '小紅書システムアカウント', copy: 'このサービスが使用するコンテンツアカウントのセッションを更新します。一般ユーザーにはログイン情報を表示しません。' },
    login: { method: 'ログイン方法', qrcode: 'QR コード', phone: '電話番号', qrAlt: '小紅書システムアカウントのログイン QR コード', qrReady: 'QR コードを生成して小紅書でスキャン', qrStart: 'QR コードを生成', qrRestart: '再生成', zone: '国番号', phoneNumber: '電話番号', code: '確認コード', codePlaceholder: 'SMS コードを入力', sendCode: 'コードを送信', verify: '確認してログイン', cookieLabel: 'Cookie', cookieNote: 'Cookie は現在の TravelMind サービスにのみ送信され、ブラウザには保存されません。', cookieSubmit: 'Cookie を確認', currentUser: '現在のアカウント：{{name}}', continuePlanning: '戻って再計画する' },
    states: { preparing: '準備中', waiting_scan: 'スキャン待ち', waiting_confirm: 'スマートフォンの確認待ち', code_sent: 'コード送信済み', authenticating: '確認中', success: 'システムアカウント更新済み', expired: 'ログイン期限切れ', error: 'ログイン失敗' },
    logout: { title: 'ログイン状態を消去', copy: '管理者が再ログインするまで旅行コンテンツの検索は停止します。', action: 'ログイン状態を消去', confirm: '現在の小紅書システムアカウントのログイン状態を消去しますか？', success: '小紅書のログイン状態を消去しました' },
    errors: { access: '管理者認証に失敗しました', request: 'アカウント管理のリクエストに失敗しました', qrcode: 'QR コードを読み込めません。再生成してください。', logout: 'ログイン状態を消去できませんでした。もう一度お試しください。' },
  },
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

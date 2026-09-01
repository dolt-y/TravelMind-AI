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
  planner: { destination: '目的地', destinationPlaceholder: '想去哪里？', preferences: '旅行偏好', preferencesPlaceholder: '美食、徒步、建筑、亲子…', noteCount: '参考笔记', notes: '{{count}} 篇', resultLanguage: '结果语言', submit: '开始规划' },
  plan: { eyebrow: '规划新的旅程', title: '说说你想去哪里', copy: '填写目的地和旅行偏好，我们会帮你整理更合适的游玩选择。', pipelineEyebrow: '探索过程', pipelineTitle: '从想法到旅行清单', pipelineCopy: '我们会寻找旅行灵感、整理地点信息，并为你生成一份清晰的目的地清单。' },
  pipeline: { search: '寻找旅行灵感', searchCopy: '了解目的地有哪些值得体验的地方', extract: '整理推荐地点', extractCopy: '从旅行分享中找到更符合你偏好的选择', poi: '确认地点信息', poiCopy: '补充地址、位置、评分和图片', persist: '生成旅行清单', persistCopy: '把这次探索整理成方便继续查看的结果' },
  planning: { eyebrow: '正在准备旅行灵感', title: '正在探索 {{city}}', copy: '我们正在认真寻找适合你的地方，这通常需要一点时间。', failed: '本次规划没有完成', back: '返回修改条件' },
  results: { saved: '本次旅行灵感', title: '{{city}}旅行候选', summary: '参考 {{notes}} 篇旅行分享，整理出 {{places}} 个地点', retry: '重新规划', placesEyebrow: '推荐地点', places: '值得进一步了解的地方', favorite: '收藏地点', unfavorite: '取消收藏', reservation: '建议预约', addressPending: '地点地址暂未完善', liveData: '出行参考', weather: '目的地天气', hotels: '住宿选择', weatherEmpty: '暂时没有天气信息', hotelEmpty: '暂时没有住宿信息', perNight: '/晚', noPlaces: '没有找到合适的地点，请调整偏好后重试。', emptyTitle: '还没有旅行结果', emptyCopy: '先选择目的地，开始你的第一次旅行探索。', start: '开始规划' },
  library: { eyebrow: '我的资料', title: '继续上一次旅行探索', copy: '查看你最近整理的目的地和旅行灵感。', emptyTitle: '这里还是空的', emptyCopy: '完成一次目的地探索后，行程会出现在这里。', start: '开始规划', latest: '最近一次探索', summary: '{{notes}} 篇旅行分享 · {{places}} 个地点', noPreference: '随心探索', open: '查看行程' },
  settings: { eyebrow: '账户设置', title: '偏好与账户', copy: '管理界面语言和旅行灵感来源。', language: '界面语言', languageCopy: '切换导航、页面和操作文案', xhs: '小红书连接', xhsCopy: '连接后可以发现更多真实旅行灵感', manage: '管理连接' },
  login: {
    eyebrow: '旅行灵感来源', title: '连接小红书', copy: '选择一种登录方式，发现更多真实旅行分享。', method: '登录方式', qrcode: '二维码', phone: '手机号', qrAlt: '小红书登录二维码', qrReady: '生成二维码后使用小红书扫码', qrStart: '生成二维码', qrRestart: '重新生成', phoneNumber: '手机号码', code: '验证码', codePlaceholder: '输入短信验证码', sendCode: '发送验证码', verify: '验证并登录', cookieLabel: 'Cookie', cookieNote: '登录信息仅用于本次连接，输入内容不会在页面中保留。', cookieSubmit: '使用 Cookie 登录', error: '登录请求失败',
    states: { preparing: '正在准备', waiting_scan: '等待扫码', waiting_confirm: '等待手机确认', code_sent: '验证码已发送', authenticating: '正在验证', success: '登录成功', expired: '登录已过期', error: '登录失败' },
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
  planner: { destination: 'Destination', destinationPlaceholder: 'Where do you want to go?', preferences: 'Travel preferences', preferencesPlaceholder: 'Food, hiking, architecture, family…', noteCount: 'Reference notes', notes: '{{count}} notes', resultLanguage: 'Result language', submit: 'Start planning' },
  plan: { eyebrow: 'PLAN A NEW JOURNEY', title: 'Tell us where you want to go', copy: 'Add a destination and your travel style, and we will organize ideas that suit you.', pipelineEyebrow: 'HOW IT WORKS', pipelineTitle: 'From an idea to a travel shortlist', pipelineCopy: 'We find inspiration, organize places, confirm useful details, and shape a clear shortlist for you.' },
  pipeline: { search: 'Find travel inspiration', searchCopy: 'Learn what is worth experiencing at your destination', extract: 'Organize recommended places', extractCopy: 'Find options that better match your travel style', poi: 'Confirm place details', poiCopy: 'Add addresses, locations, ratings, and photos', persist: 'Build your travel shortlist', persistCopy: 'Turn this exploration into an easy result to revisit' },
  planning: { eyebrow: 'PREPARING TRAVEL IDEAS', title: 'Exploring {{city}}', copy: 'We are carefully looking for places that suit you. This usually takes a moment.', failed: 'Planning could not be completed', back: 'Edit preferences' },
  results: { saved: 'YOUR TRAVEL IDEAS', title: '{{city}} travel candidates', summary: '{{notes}} travel stories led to {{places}} places', retry: 'Plan again', placesEyebrow: 'RECOMMENDED PLACES', places: 'Places worth a closer look', favorite: 'Favorite place', unfavorite: 'Remove favorite', reservation: 'Reservation suggested', addressPending: 'Address not available yet', liveData: 'TRAVEL CONDITIONS', weather: 'Destination weather', hotels: 'Places to stay', weatherEmpty: 'Weather is not available yet', hotelEmpty: 'Accommodation is not available yet', perNight: '/night', noPlaces: 'No suitable places were found. Adjust your preferences and try again.', emptyTitle: 'No trip ideas yet', emptyCopy: 'Choose a destination and begin your first exploration.', start: 'Start planning' },
  library: { eyebrow: 'MY TRIPS', title: 'Continue your latest exploration', copy: 'See the destinations and travel ideas you recently prepared.', emptyTitle: 'Nothing here yet', emptyCopy: 'Complete a destination search and your trip will appear here.', start: 'Plan a trip', latest: 'Latest exploration', summary: '{{notes}} travel stories · {{places}} places', noPreference: 'Explore freely', open: 'View trip' },
  settings: { eyebrow: 'ACCOUNT', title: 'Preferences and account', copy: 'Manage your interface language and travel inspiration connection.', language: 'Interface language', languageCopy: 'Change navigation and page copy', xhs: 'Xiaohongshu connection', xhsCopy: 'Connect to discover more real travel inspiration', manage: 'Manage connection' },
  login: { eyebrow: 'TRAVEL INSPIRATION', title: 'Connect Xiaohongshu', copy: 'Choose a sign-in method to discover more real travel stories.', method: 'Login method', qrcode: 'QR code', phone: 'Phone', qrAlt: 'Xiaohongshu login QR code', qrReady: 'Generate a code and scan it with Xiaohongshu', qrStart: 'Generate code', qrRestart: 'Generate again', phoneNumber: 'Phone number', code: 'Verification code', codePlaceholder: 'Enter SMS code', sendCode: 'Send code', verify: 'Verify and log in', cookieLabel: 'Cookie', cookieNote: 'Login details are used only for this connection and are cleared from the page afterward.', cookieSubmit: 'Log in with Cookie', error: 'Login request failed', states: { preparing: 'Preparing', waiting_scan: 'Waiting for scan', waiting_confirm: 'Waiting for confirmation', code_sent: 'Code sent', authenticating: 'Authenticating', success: 'Signed in', expired: 'Login expired', error: 'Login failed' } },
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
  planner: { destination: '目的地', destinationPlaceholder: 'どこへ行きますか？', preferences: '旅行の好み', preferencesPlaceholder: 'グルメ、ハイキング、建築、家族…', noteCount: '参照記事', notes: '{{count}} 件', resultLanguage: '結果の言語', submit: '計画を始める' },
  plan: { eyebrow: '新しい旅を計画', title: '行きたい場所を教えてください', copy: '目的地と旅行の好みを入力すると、あなたに合う場所を整理します。', pipelineEyebrow: '旅ができるまで', pipelineTitle: 'アイデアから旅の候補へ', pipelineCopy: '旅のヒントを探し、場所を整理し、役立つ情報を確認して候補を作ります。' },
  pipeline: { search: '旅のヒントを探す', searchCopy: '目的地で体験したいことを見つけます', extract: 'おすすめ場所を整理', extractCopy: '旅行の好みに合う場所を選びます', poi: '場所の情報を確認', poiCopy: '住所、位置、評価、写真を補足します', persist: '旅の候補を作成', persistCopy: '今回の探索を見やすくまとめます' },
  planning: { eyebrow: '旅のアイデアを準備中', title: '{{city}}を探索中', copy: 'あなたに合う場所を探しています。少しだけお待ちください。', failed: '計画を完了できませんでした', back: '条件を変更する' },
  results: { saved: '今回の旅のアイデア', title: '{{city}}の旅行候補', summary: '{{notes}} 件の旅行記事から {{places}} 地点を整理しました', retry: 'もう一度計画', placesEyebrow: 'おすすめ場所', places: '詳しく知りたい場所', favorite: 'お気に入り', unfavorite: 'お気に入りを解除', reservation: '予約推奨', addressPending: '住所は準備中です', liveData: '旅の参考', weather: '目的地の天気', hotels: '宿泊先', weatherEmpty: '天気情報はまだありません', hotelEmpty: '宿泊情報はまだありません', perNight: '/泊', noPlaces: '場所が見つかりません。好みを変えてお試しください。', emptyTitle: '旅の候補がありません', emptyCopy: '目的地を選んで最初の探索を始めましょう。', start: '計画を始める' },
  library: { eyebrow: 'マイトリップ', title: '前回の探索を続ける', copy: '最近整理した目的地と旅のアイデアを確認できます。', emptyTitle: 'まだ何もありません', emptyCopy: '目的地を探索すると旅がここに表示されます。', start: '旅を計画', latest: '最近の探索', summary: '{{notes}} 件の旅行記事 · {{places}} 地点', noPreference: '自由に探索', open: '旅を見る' },
  settings: { eyebrow: 'アカウント', title: '好みとアカウント', copy: '表示言語と旅の情報源を管理します。', language: '表示言語', languageCopy: 'ナビゲーションとページの言語を変更', xhs: '小紅書との接続', xhsCopy: '接続すると、より多くの旅行アイデアを見つけられます', manage: '接続を管理' },
  login: { eyebrow: '旅の情報源', title: '小紅書に接続', copy: 'ログイン方法を選び、より多くの旅行記事を見つけましょう。', method: 'ログイン方法', qrcode: 'QR コード', phone: '電話番号', qrAlt: '小紅書ログイン QR コード', qrReady: 'QR コードを生成して小紅書でスキャン', qrStart: 'QR を生成', qrRestart: '再生成', phoneNumber: '電話番号', code: '確認コード', codePlaceholder: 'SMS コードを入力', sendCode: 'コードを送信', verify: '確認してログイン', cookieLabel: 'Cookie', cookieNote: 'ログイン情報は今回の接続にのみ使用され、入力内容はページに残りません。', cookieSubmit: 'Cookie でログイン', error: 'ログインに失敗しました', states: { preparing: '準備中', waiting_scan: 'スキャン待ち', waiting_confirm: '確認待ち', code_sent: 'コード送信済み', authenticating: '確認中', success: 'ログイン成功', expired: '期限切れ', error: 'ログイン失敗' } },
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

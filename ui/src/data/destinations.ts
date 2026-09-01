export interface DestinationPreset {
  city: string
  cityKey: string
  keywords: string
  keywordsKey: string
  image: string
}

export const destinationPresets: DestinationPreset[] = [
  {
    city: '阿马尔菲',
    cityKey: 'destinations.amalfi',
    keywords: '海岸自驾',
    keywordsKey: 'destinations.coast',
    image: '/assets/travel/amalfi-coast.jpg',
  },
  {
    city: '京都',
    cityKey: 'destinations.kyoto',
    keywords: '古都建筑',
    keywordsKey: 'destinations.culture',
    image: '/assets/travel/kyoto.jpg',
  },
  {
    city: '冰岛',
    cityKey: 'destinations.iceland',
    keywords: '极光自然',
    keywordsKey: 'destinations.aurora',
    image: '/assets/travel/iceland-aurora.jpg',
  },
  {
    city: '瑞士',
    cityKey: 'destinations.switzerland',
    keywords: '湖泊徒步',
    keywordsKey: 'destinations.alpine',
    image: '/assets/travel/switzerland-lake.jpg',
  },
  {
    city: '挪威',
    cityKey: 'destinations.norway',
    keywords: '海岸徒步',
    keywordsKey: 'destinations.hiking',
    image: '/assets/travel/travelmind-hero.jpg',
  },
]

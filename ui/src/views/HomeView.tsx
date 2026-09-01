import { BusinessFlowShowcase } from '../components/home/BusinessFlowShowcase'
import { DestinationShowcase } from '../components/home/DestinationShowcase'
import { HomeHero } from '../components/home/HomeHero'

export function HomeView() {
  return (
    <div className="home-page">
      <HomeHero />
      <DestinationShowcase />
      <BusinessFlowShowcase />
    </div>
  )
}

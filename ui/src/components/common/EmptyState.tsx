import type { LucideIcon } from 'lucide-react'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel: string
  actionTo: string
}

export function EmptyState({ icon: Icon, title, description, actionLabel, actionTo }: EmptyStateProps) {
  return (
    <section className="empty-state">
      <Icon size={34} strokeWidth={1.6} aria-hidden="true" />
      <h1>{title}</h1>
      <p>{description}</p>
      <Link className="button button--primary" to={actionTo}>
        {actionLabel}
        <ArrowRight size={17} aria-hidden="true" />
      </Link>
    </section>
  )
}

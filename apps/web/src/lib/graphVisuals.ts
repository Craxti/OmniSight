import type { LucideIcon } from 'lucide-react'
import {
  AppWindow,
  Boxes,
  Briefcase,
  Cloud,
  Database,
  Globe,
  HardDrive,
  Inbox,
  Network,
  Server,
  Wrench,
} from 'lucide-react'
import type { RelationType } from '@/shared/constants'

export type CiTypeVisual = {
  icon: LucideIcon
  accent: string
  iconBg: string
}

export type RelationVisual = {
  color: string
  dash?: string
  strokeWidth: number
}

const DEFAULT_CI_VISUAL: CiTypeVisual = {
  icon: Boxes,
  accent: '#818cf8',
  iconBg: 'rgba(99, 102, 241, 0.22)',
}

const CI_TYPE_VISUALS: Record<string, CiTypeVisual> = {
  'Business Service': {
    icon: Briefcase,
    accent: '#f59e0b',
    iconBg: 'rgba(245, 158, 11, 0.2)',
  },
  Application: {
    icon: AppWindow,
    accent: '#6366f1',
    iconBg: 'rgba(99, 102, 241, 0.22)',
  },
  Container: {
    icon: Boxes,
    accent: '#8b5cf6',
    iconBg: 'rgba(139, 92, 246, 0.2)',
  },
  Database: {
    icon: Database,
    accent: '#3b82f6',
    iconBg: 'rgba(59, 130, 246, 0.2)',
  },
  Server: {
    icon: Server,
    accent: '#94a3b8',
    iconBg: 'rgba(148, 163, 184, 0.18)',
  },
  'Virtual Machine': {
    icon: Cloud,
    accent: '#06b6d4',
    iconBg: 'rgba(6, 182, 212, 0.18)',
  },
  Queue: {
    icon: Inbox,
    accent: '#f97316',
    iconBg: 'rgba(249, 115, 22, 0.18)',
  },
  'Network Element': {
    icon: Network,
    accent: '#14b8a6',
    iconBg: 'rgba(20, 184, 166, 0.18)',
  },
  'External Service': {
    icon: Globe,
    accent: '#a855f7',
    iconBg: 'rgba(168, 85, 247, 0.18)',
  },
  'Technical Component': {
    icon: Wrench,
    accent: '#22c55e',
    iconBg: 'rgba(34, 197, 94, 0.18)',
  },
  'Storage Volume': {
    icon: HardDrive,
    accent: '#64748b',
    iconBg: 'rgba(100, 116, 139, 0.18)',
  },
}

export const RELATION_VISUALS: Record<RelationType, RelationVisual> = {
  depends_on: { color: '#3b82f6', strokeWidth: 2 },
  hosted_on: { color: '#a855f7', dash: '7 4', strokeWidth: 1.75 },
  uses: { color: '#f97316', dash: '2 5', strokeWidth: 1.75 },
  part_of: { color: '#06b6d4', strokeWidth: 1.75 },
  linked_to: { color: '#64748b', dash: '4 3 1 3', strokeWidth: 1.5 },
  affects: { color: '#ef4444', strokeWidth: 1.75 },
  reserves: { color: '#22c55e', dash: '9 5', strokeWidth: 1.75 },
}

export function getCiTypeVisual(type: string): CiTypeVisual {
  return CI_TYPE_VISUALS[type] ?? DEFAULT_CI_VISUAL
}

export function getRelationVisual(relationType: string): RelationVisual {
  return RELATION_VISUALS[relationType as RelationType] ?? {
    color: '#94a3b8',
    strokeWidth: 1.5,
  }
}

/** Цвета маркеров подсветки узлов — совпадают с --graph-marker-* в theme.css */
export const GRAPH_NODE_MARKER_COLORS = {
  root: 'var(--graph-marker-root)',
  businessPath: 'var(--graph-marker-business-path)',
  impact: 'var(--graph-marker-impact)',
  components: 'var(--graph-marker-components)',
} as const

export const GRAPH_PATH_EDGE_COLOR = GRAPH_NODE_MARKER_COLORS.businessPath

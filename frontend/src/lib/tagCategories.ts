interface CategoryDefinition {
  label: string
  tags: string[]
}

// A fixed, hand-curated map from known tag words to a mood/theme grouping.
// Deliberately simple (no clustering infra) — Gemini's auto-tagger already
// reuses existing tags (see app/tagging.py), so the vocabulary grows slowly
// and this list is cheap to extend by hand as new tags show up in "other".
const CATEGORY_DEFINITIONS: CategoryDefinition[] = [
  {
    label: 'strength & grit',
    tags: [
      'persistence',
      'perseverance',
      'resilience',
      'strength',
      'determination',
      'control',
      'patience',
      'discipline',
      'endurance',
      'willpower',
      'grit',
      'courage',
      'inner strength',
      'mental control',
      'stoicism',
      'empowerment',
    ],
  },
  {
    label: 'purpose & meaning',
    tags: [
      'purpose',
      'meaning',
      'philosophy',
      'wisdom',
      'introspection',
      'reflection',
      'existentialism',
      'existence',
      'mortality',
      'life',
      'morality',
      'mindfulness',
      'perception',
      'imagination',
    ],
  },
  {
    label: 'hope & motivation',
    tags: [
      'motivation',
      'hope',
      'passion',
      'achievement',
      'inspiration',
      'success',
      'ambition',
      'opportunity',
      'dedication',
      'overcoming',
      'impossible',
      'transformation',
      'growth',
      'progress',
    ],
  },
  {
    label: 'freedom & choice',
    tags: ['freedom', 'choice', 'responsibility', 'autonomy', 'action', 'work', 'beginning'],
  },
  {
    label: 'difficult feelings',
    tags: ['suffering', 'anxiety', 'fear', 'corruption', 'darkness', 'burden', 'caution', 'mind'],
  },
]

const OTHER_LABEL = 'other'

const CATEGORY_BY_TAG = new Map(
  CATEGORY_DEFINITIONS.flatMap((category) => category.tags.map((tag) => [tag, category.label])),
)

export interface TagGroup<T> {
  label: string
  items: T[]
}

export function groupTagsByCategory<T extends { tag: string }>(items: T[]): TagGroup<T>[] {
  const buckets = new Map<string, T[]>()
  for (const item of items) {
    const label = CATEGORY_BY_TAG.get(item.tag.toLowerCase()) ?? OTHER_LABEL
    const bucket = buckets.get(label)
    if (bucket) bucket.push(item)
    else buckets.set(label, [item])
  }

  const orderedLabels = [...CATEGORY_DEFINITIONS.map((c) => c.label), OTHER_LABEL]
  return orderedLabels.flatMap((label) => {
    const bucketItems = buckets.get(label)
    return bucketItems ? [{ label, items: bucketItems }] : []
  })
}

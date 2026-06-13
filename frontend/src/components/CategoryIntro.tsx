interface CategoryIntroProps {
  name: string
  definition: string
  interpretation: string
}

export function CategoryIntro({ name, definition, interpretation }: CategoryIntroProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <h2 className="font-heading text-lg leading-snug font-medium tracking-tight text-foreground">
        {name}
      </h2>
      <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {definition}
      </p>
      <p className="max-w-2xl text-xs leading-relaxed text-muted-foreground/75">
        {interpretation}
      </p>
    </div>
  )
}

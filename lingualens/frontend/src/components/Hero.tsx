export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="paper-grain pointer-events-none absolute inset-0" aria-hidden />
      <div
        aria-hidden
        className="lens-motif pointer-events-none absolute -top-24 -right-16 size-72 opacity-70 md:size-96"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-28 -left-20 size-64 rounded-full bg-amber/20 blur-3xl"
      />

      <div className="relative mx-auto max-w-5xl px-4 pt-14 pb-10 text-center md:pt-20 md:pb-14">
        <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-vermilion/30 bg-vermilion/5 px-3 py-1 text-xs font-medium tracking-wide text-vermilion uppercase">
          <span aria-hidden className="size-1.5 rounded-full bg-vermilion" />
          OCR · AI · Translation — from one snapshot
        </p>
        <h1 className="mx-auto max-w-2xl text-4xl leading-[1.05] font-bold tracking-tight text-balance md:text-6xl">
          See any document.{" "}
          <span className="bg-linear-to-r from-vermilion to-amber bg-clip-text text-transparent">
            Understand it
          </span>{" "}
          your language.
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-balance text-muted-foreground md:text-lg">
          Snap or drop a medicine label, a government form, a signboard — and
          get a plain-language explanation tailored to you, with audio and
          follow-up questions.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs text-muted-foreground">
          <span className="rounded-full border border-border bg-card px-3 py-1">
            English · हिंदी · தமிழ்
          </span>
          <span className="rounded-full border border-border bg-card px-3 py-1">
            Images &amp; webcam
          </span>
          <span className="rounded-full border border-border bg-card px-3 py-1">
            Voice questions
          </span>
        </div>
      </div>
    </section>
  )
}
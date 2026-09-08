import ReactMarkdown, { type Components } from "react-markdown"

const mdComponents: Components = {
  h1: ({ children }) => (
    <h3 className="mt-4 mb-1 text-lg font-semibold tracking-tight">
      {children}
    </h3>
  ),
  h2: ({ children, ...props }) => (
    <h4 className="mt-4 mb-1 text-base font-semibold tracking-tight" {...props}>
      {children}
    </h4>
  ),
  h3: ({ children }) => (
    <h4 className="mt-3 mb-1 text-base font-semibold tracking-tight">
      {children}
    </h4>
  ),
  p: ({ children }) => <p className="my-2 leading-relaxed">{children}</p>,
  ul: ({ children }) => (
    <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="my-2 list-decimal space-y-1 pl-5">{children}</ol>
  ),
  li: ({ children }) => <li>{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em>{children}</em>,
  blockquote: ({ children }) => (
    <blockquote className="my-2 border-l-2 border-vermilion pl-4 italic">
      {children}
    </blockquote>
  ),
  code: ({ children }) => (
    <code className="rounded bg-muted px-1.5 py-0.5 text-[0.85em]">
      {children}
    </code>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-vermilion underline underline-offset-2">
      {children}
    </a>
  ),
}

export function Markdown({ children }: { children: string }) {
  return (
    <div className="text-sm leading-relaxed md:text-[0.95rem]">
      <ReactMarkdown components={mdComponents}>{children}</ReactMarkdown>
    </div>
  )
}
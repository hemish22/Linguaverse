import { Component, type ErrorInfo, type PropsWithChildren, type ReactNode } from "react"
import { AlertTriangle, RefreshCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface ErrorBoundaryProps extends PropsWithChildren {
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  message: string
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, message: "" }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, message: error.message }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, info)
  }

  reset = () => {
    this.setState({ hasError: false, message: "" })
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <Card className="mx-auto w-full max-w-xl">
            <CardContent className="flex flex-col items-center gap-4 py-10 text-center">
              <AlertTriangle className="size-10 text-amber-500" aria-hidden />
              <div className="space-y-1">
                <p className="text-base font-semibold">Something went wrong rendering results</p>
                <p className="text-sm text-muted-foreground">
                  Please try again. If it keeps happening, upload the document once more or paste the text.
                </p>
              </div>
              <Button onClick={this.reset}>
                <RefreshCcw data-icon="inline-start" />
                Reset
              </Button>
            </CardContent>
          </Card>
        )
      )
    }
    return this.props.children
  }
}
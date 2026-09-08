"use client"

import { Slider as SliderPrimitive } from "@base-ui/react/slider"
import { cn } from "cn"

function Slider({
  className,
  ...props
}: SliderPrimitive.Root.Props<number>) {
  return (
    <SliderPrimitive.Root
      data-slot="slider"
      className={cn(
        "group/slider relative flex w-full items-center touch-none select-none",
        className,
      )}
      {...props}
    >
      <SliderPrimitive.Control className="h-full w-full grow cursor-pointer">
        <SliderPrimitive.Track className="relative h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <SliderPrimitive.Indicator className="absolute top-0 left-0 h-full bg-vermilion transition-[width] duration-75" />
          <SliderPrimitive.Thumb className="absolute top-1/2 size-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-card shadow-sm ring-2 ring-vermilion transition-opacity focus:opacity-100 focus:ring-3 focus:ring-ring/50 focus:outline-hidden group-data-[dragging]:opacity-100 data-[hovered]:opacity-100 sm:opacity-0" />
        </SliderPrimitive.Track>
      </SliderPrimitive.Control>
    </SliderPrimitive.Root>
  )
}

export { Slider }
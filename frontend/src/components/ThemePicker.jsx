import React, { useEffect, useMemo, useState } from "react";
import { palettes } from "../mock";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../components/ui/tooltip";
import { Button } from "../components/ui/button";
import { Check, Palette } from "lucide-react";

function applyThemeVars(theme) {
  const root = document.documentElement;
  root.style.setProperty("--msk-color-base", theme.baseColor);
  root.style.setProperty("--msk-bg-base", theme.baseBg);
  root.style.setProperty("--msk-color", theme.color);
  root.style.setProperty("--msk-bg", theme.bg);
  root.style.setProperty("--msk-accent", theme.accent);
  root.style.setProperty("--msk-subtle", theme.subtle);
}

export default function ThemePicker({ onApplied }) {
  const [active, setActive] = useState(() => {
    const saved = localStorage.getItem("timepage_theme");
    return saved ? JSON.parse(saved) : palettes[0];
  });

  useEffect(() => {
    applyThemeVars(active);
  }, []);

  const handleApply = (p) => {
    setActive(p);
    applyThemeVars(p);
    localStorage.setItem("timepage_theme", JSON.stringify(p));
    onApplied?.(p);
  };

  const gridCols = useMemo(() => (palettes.length > 6 ? "grid-cols-3 md:grid-cols-6" : "grid-cols-3 md:grid-cols-4"), []);

  return (
    <section id="themes" className="w-full">
      <div className="mb-6 flex items-center gap-2">
        <Palette size={18} className="opacity-70" />
        <h2 className="text-[min(4vh,_min(5vw,_28px))] font-semibold tracking-tight">Curated color palettes</h2>
      </div>

      <div className={`grid ${gridCols} gap-4`}>
        {palettes.map((p) => {
          const isActive = p.id === active.id;
          return (
            <TooltipProvider key={p.id}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Card data-testid={`palette-card-${p.id}`}
                    className={`tp-card relative transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-md cursor-pointer ${
                      isActive ? "ring-2 ring-[var(--msk-accent)]" : "ring-1 ring-border"
                    }`}
                    onClick={() => handleApply(p)}
                    style={{ background: p.bg }}
                  >
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm" style={{ color: p.color }}>{p.name}</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex h-14 w-full overflow-hidden rounded-md">
                        <div className="h-full w-1/2" style={{ background: p.accent }} />
                        <div className="h-full w-1/2" style={{ background: p.subtle }} />
                      </div>
                      <div className="mt-3 flex items-center justify-between">
                        <div className="text-xs text-muted-foreground" style={{ color: p.subtle }}>
                          {p.color}
                        </div>
                        {isActive ? (
                          <div className="flex items-center gap-1 text-[var(--msk-accent)] text-xs">
                            <Check size={14} /> Active
                          </div>
                        ) : (
                          <Button variant="secondary" size="sm">Apply</Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </TooltipTrigger>
                <TooltipContent side="top" align="center">
                  <span>Click to apply "{p.name}" theme</span>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          );
        })}
      </div>

      <div className="mt-8">
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle className="text-base">Live preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-lg p-4" style={{ background: "var(--msk-bg)", color: "var(--msk-color)" }}>
                <div className="text-sm opacity-70">Today</div>
                <div className="mt-1 text-[min(5vh,_min(8vw,_34px))] font-semibold">12:30 Lunch</div>
                <div className="mt-2 text-sm" style={{ color: "var(--msk-subtle)" }}>Downtown, 20 min away</div>
              </div>
              <div className="rounded-lg p-4" style={{ background: "var(--msk-accent)", color: "white" }}>
                <div className="text-sm opacity-90">Weather</div>
                <div className="mt-1 text-2xl font-semibold">22° C · Clear</div>
                <div className="mt-2 text-xs opacity-80">Feels 21°, Rain 0%</div>
              </div>
              <div className="rounded-lg p-4" style={{ background: "#ffffff", color: "var(--msk-color)", border: "1px solid var(--border)" }}>
                <div className="text-sm" style={{ color: "var(--msk-subtle)" }}>Focus</div>
                <div className="mt-1 text-xl font-semibold">Deep Work</div>
                <div className="mt-2 text-xs" style={{ color: "var(--msk-subtle)" }}>2h block · Silent</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
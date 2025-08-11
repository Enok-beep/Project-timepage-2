import React, { useEffect, useState } from "react";
import ThemePicker from "../components/ThemePicker";
import { features, microcopy, palettes as mockPalettes } from "../mock";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Input } from "../components/ui/input";
import * as Icons from "lucide-react";
import { getPalettes, savePreference, notifyEmail } from "../lib/api";
import { useToast } from "../hooks/use-toast";

function loadInitialTheme() {
  const saved = localStorage.getItem("timepage_theme");
  const theme = saved ? JSON.parse(saved) : mockPalettes[0];
  const root = document.documentElement;
  root.style.setProperty("--msk-color-base", theme.baseColor);
  root.style.setProperty("--msk-bg-base", theme.baseBg);
  root.style.setProperty("--msk-color", theme.color);
  root.style.setProperty("--msk-bg", theme.bg);
  root.style.setProperty("--msk-accent", theme.accent);
  root.style.setProperty("--msk-subtle", theme.subtle);
}

export default function Home() {
  const { toast } = useToast();
  const [palettes, setPalettes] = useState([]);
  const [email, setEmail] = useState("");

  useEffect(() => {
    loadInitialTheme();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPalettes();
        if (Array.isArray(data) && data.length) setPalettes(data);
        else setPalettes(mockPalettes);
      } catch (e) {
        setPalettes(mockPalettes);
      }
    })();
  }, []);

  const onApplyPersist = async (palette) => {
    try {
      const existingSession = localStorage.getItem("tp_session_id");
      const res = await savePreference({ sessionId: existingSession || undefined, paletteId: palette.id });
      localStorage.setItem("tp_session_id", res.session_id);
      toast({ title: "Theme saved", description: `Applied ${palette.name} for your session.` });
    } catch (e) {
      toast({ title: "Saved locally", description: "Backend unreachable. We'll sync next time.", });
    }
  };

  const onNotify = async (e) => {
    e.preventDefault();
    if (!email) return;
    try {
      await notifyEmail(email);
      setEmail("");
      toast({ title: "Thanks!", description: "We'll keep you posted." });
    } catch (err) {
      toast({ title: "Oops", description: "Could not save your email. Try again later." });
    }
  };

  return (
    <div className="min-h-screen" style={{ background: "var(--msk-bg)", color: "var(--msk-color)" }}>
      <header className="sticky top-0 z-30 backdrop-blur-md" style={{ background: "color-mix(in srgb, var(--msk-bg) 85%, transparent)" }}>
        <div className="mx-auto max-w-6xl px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 select-none">
            <div className="h-5 w-5 rounded-sm" style={{ background: "var(--msk-accent)" }} />
            <span className="text-sm tracking-wide">Timepage Clone</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm opacity-80">
            <a href="#features" className="hover:opacity-100 transition-opacity">Features</a>
            <a href="#themes" className="hover:opacity-100 transition-opacity">Themes</a>
            <a href="#download" className="hover:opacity-100 transition-opacity">Download</a>
          </nav>
          <div className="flex items-center gap-2">
            <Button className="rounded-md" style={{ background: "var(--msk-accent)", color: "#fff" }}>
              Get the app
            </Button>
          </div>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="mx-auto max-w-6xl px-5 pt-14 pb-12 md:pt-24 md:pb-16">
          <h1 className="leading-tight font-semibold" style={{ fontSize: "min(6vh, min(7vw, 56px))" }}>
            {microcopy.heroHeading}
          </h1>
          <p className="mt-3 text-[15px] md:text-base opacity-80 max-w-2xl">
            {microcopy.heroSub}
          </p>
          <div className="mt-6 flex items-center gap-3">
            <Button className="rounded-md" style={{ background: "var(--msk-accent)", color: "#fff" }} onClick={() => {
              const el = document.getElementById("themes");
              el?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}>
              {microcopy.ctaPrimary}
            </Button>
            <Button variant="secondary" className="rounded-md" onClick={() => {
              const el = document.getElementById("features");
              el?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}>
              {microcopy.ctaSecondary}
            </Button>
          </div>

          {/* App preview banner */}
          <div className="mt-10">
            <Card className="overflow-hidden">
              <CardContent className="p-0">
                <div className="grid grid-cols-1 md:grid-cols-3">
                  <div className="p-6" style={{ background: "var(--msk-accent)", color: "#fff" }}>
                    <div className="text-sm opacity-90">Agenda</div>
                    <div className="mt-2 text-2xl font-semibold">Today at a glance</div>
                    <div className="mt-3 text-xs opacity-90">Elegant typography and subtle color accents keep focus on what matters.</div>
                  </div>
                  <div className="p-6" style={{ background: "#ffffff", color: "var(--msk-color)" }}>
                    <div className="text-sm" style={{ color: "var(--msk-subtle)" }}>Heatmap</div>
                    <div className="mt-2 text-xl font-semibold">See your rhythm</div>
                    <div className="mt-3 text-xs" style={{ color: "var(--msk-subtle)" }}>Busy days glow gently so your free time is obvious.</div>
                  </div>
                  <div className="p-6" style={{ background: "var(--msk-bg)", color: "var(--msk-color)" }}>
                    <div className="text-sm" style={{ color: "var(--msk-subtle)" }}>Weather</div>
                    <div className="mt-2 text-xl font-semibold">Plan with context</div>
                    <div className="mt-3 text-xs" style={{ color: "var(--msk-subtle)" }}>Weather and travel blend right into your day.</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <Separator />

        {/* Features */}
        <section id="features" className="mx-auto max-w-6xl px-5 pt-12 pb-8 md:pt-16 md:pb-12">
          <h2 className="text-[min(4vh,_min(5vw,_28px))] font-semibold tracking-tight">Designed for clarity</h2>
          <p className="mt-2 text-sm md:text-base opacity-80 max-w-2xl">Micro-animations, responsive typography and a color system that adapts to your context.</p>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => {
              const Icon = Icons[f.icon] || Icons.Sparkles;
              return (
                <Card key={f.id} className="transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-md flex items-center justify-center" style={{ background: "var(--msk-accent)", color: "#fff" }}>
                        <Icon size={16} />
                      </div>
                      <div className="text-base font-medium">{f.title}</div>
                    </div>
                    <div className="mt-3 text-sm opacity-80">{f.description}</div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

        <Separator />

        {/* Theme Picker */}
        <section className="mx-auto max-w-6xl px-5 pt-12 pb-16 md:pt-16 md:pb-24">
          <ThemePicker palettesData={palettes} onApplied={onApplyPersist} />
        </section>

        <Separator />

        {/* Download section (mock) */}
        <section id="download" className="mx-auto max-w-6xl px-5 pt-12 pb-16 md:pt-16 md:pb-24">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-2">
              <h2 className="text-[min(4vh,_min(5vw,_28px))] font-semibold tracking-tight">Coming soon</h2>
              <p className="mt-2 text-sm md:text-base opacity-80 max-w-2xl">This replica uses mocked content and a local theme system. We can wire up real product links and content next.</p>
              <form className="mt-6 flex items-center gap-3" onSubmit={onNotify}>
                <div className="w-full max-w-xs">
                  <Input type="email" placeholder="Enter your email" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
                <Button className="rounded-md" style={{ background: "var(--msk-accent)", color: "#fff" }} type="submit">Notify me</Button>
                <Button variant="secondary" className="rounded-md" type="button">Learn more</Button>
              </form>
            </div>
            <div className="md:justify-self-end">
              <div className="rounded-lg border p-5 text-sm" style={{ background: "#fff", color: "var(--msk-color)" }}>
                <div className="opacity-70">Mock data</div>
                <ul className="mt-2 list-disc pl-4 space-y-1 opacity-80">
                  <li>Palettes seeded in DB on backend</li>
                  <li>Preferences saved per session</li>
                  <li>Emails captured server-side</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="mx-auto max-w-6xl px-5 py-10 text-sm opacity-80">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-center gap-2 select-none">
              <div className="h-4 w-4 rounded-sm" style={{ background: "var(--msk-accent)" }} />
              <span>Timepage Clone</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#features" className="hover:opacity-100 transition-opacity">Features</a>
              <a href="#themes" className="hover:opacity-100 transition-opacity">Themes</a>
              <a href="#download" className="hover:opacity-100 transition-opacity">Download</a>
            </div>
          </div>
          <div className="mt-6 opacity-60">© {new Date().getFullYear()} — Demo replica. All product names and images are placeholders.</div>
        </div>
      </footer>
    </div>
  );
}
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Compass, 
  Search, 
  BookOpen, 
  GitBranch, 
  Activity, 
  ArrowRight, 
  Terminal,
  Cpu,
  ShieldCheck,
  Zap
} from "lucide-react"

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/20">
      {/* Navigation */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary/10 p-2 rounded-lg">
              <Compass className="h-6 w-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight">Compass</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-foreground transition-colors">How it Works</a>
            <a href="#integrations" className="hover:text-foreground transition-colors">Integrations</a>
            <a href="#docs" className="hover:text-foreground transition-colors">Documentation</a>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="hidden sm:inline-flex">Sign In</Button>
            <Button>Get Started</Button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-24 pb-32 lg:pt-36 lg:pb-40">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
          <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary/20 opacity-20 blur-[100px]"></div>
          
          <div className="container mx-auto px-4 relative z-10 text-center">
            <Badge variant="secondary" className="mb-6 px-4 py-1.5 text-sm font-medium rounded-full border-primary/20 bg-primary/5 text-primary">
              <Zap className="w-4 h-4 mr-2 inline-block" />
              Introducing Compass 2.0
            </Badge>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 max-w-4xl mx-auto leading-[1.1]">
              The AI-Native <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary/60">
                Internal Developer Portal
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
              Discover, understand, and manage your microservices with AI. 
              Stop searching through scattered docs and start building.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="h-12 px-8 text-base rounded-full w-full sm:w-auto group">
                Start Exploring
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button size="lg" variant="outline" className="h-12 px-8 text-base rounded-full w-full sm:w-auto">
                <Terminal className="mr-2 h-4 w-4" />
                View Documentation
              </Button>
            </div>
            
            {/* Mock Search Bar */}
            <div className="mt-16 max-w-3xl mx-auto bg-card border border-border/50 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-sm">
              <div className="flex items-center px-4 py-3 border-b border-border/50 bg-muted/30">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-destructive/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
              </div>
              <div className="p-6 flex items-center gap-4">
                <Search className="h-6 w-6 text-muted-foreground" />
                <div className="flex-1 text-left">
                  <p className="text-lg text-foreground/80 font-medium">Ask Compass...</p>
                  <p className="text-sm text-muted-foreground">"Who owns the payment-gateway service?"</p>
                </div>
                <Button variant="secondary" size="sm" className="hidden sm:flex">
                  <kbd className="font-sans text-xs">⌘ K</kbd>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need to scale</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Compass brings order to your microservices chaos with intelligent features designed for modern engineering teams.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <FeatureCard 
                icon={<BookOpen className="h-6 w-6 text-blue-500" />}
                title="Service Catalog"
                description="A central registry of all your microservices, complete with ownership, metadata, and health status."
              />
              <FeatureCard 
                icon={<GitBranch className="h-6 w-6 text-green-500" />}
                title="Dependency Graph"
                description="Visualize how your services interact. Understand upstream and downstream impacts instantly."
              />
              <FeatureCard 
                icon={<Cpu className="h-6 w-6 text-purple-500" />}
                title="AI Assistant"
                description="Chat with your infrastructure. Ask questions about deployments, errors, and architecture."
              />
              <FeatureCard 
                icon={<Activity className="h-6 w-6 text-red-500" />}
                title="Health Metrics"
                description="Real-time monitoring of service health, deployment frequency, and DORA metrics."
              />
              <FeatureCard 
                icon={<ShieldCheck className="h-6 w-6 text-amber-500" />}
                title="Golden Paths"
                description="Scaffold new services in seconds using standardized, secure, and compliant templates."
              />
              <FeatureCard 
                icon={<Search className="h-6 w-6 text-cyan-500" />}
                title="Global Search"
                description="Find anything across your entire engineering organization with semantic vector search."
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 relative overflow-hidden">
          <div className="absolute inset-0 bg-primary/5"></div>
          <div className="container mx-auto px-4 relative z-10 text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Ready to navigate your architecture?</h2>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
              Join forward-thinking engineering teams who use Compass to build faster and break less.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto">
              <Input type="email" placeholder="Enter your work email" className="h-12 rounded-full bg-background" />
              <Button size="lg" className="h-12 px-8 rounded-full w-full sm:w-auto shrink-0">
                Get Early Access
              </Button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 bg-background py-12">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-primary" />
            <span className="font-semibold text-lg">Compass</span>
          </div>
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Compass Inc. All rights reserved.
          </p>
          <div className="flex gap-4 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
            <a href="#" className="hover:text-foreground transition-colors">Terms</a>
            <a href="#" className="hover:text-foreground transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <Card className="border-border/50 bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors duration-300">
      <CardHeader>
        <div className="mb-4 bg-background w-12 h-12 rounded-lg flex items-center justify-center border border-border/50 shadow-sm">
          {icon}
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-base leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  )
}

export default App

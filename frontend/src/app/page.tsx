"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Logo } from "@/components/brand/logo";
import {
  Gamepad2,
  Shield,
  Trophy,
  Brain,
  Lock,
  Unlock,
  ArrowRight,
  Sparkles,
  Users,
  Code,
  Target,
} from "lucide-react";

const features = [
  {
    icon: Lock,
    title: "5 Progressive Levels",
    description:
      "From naive prompts to architectural separation. Each level presents a more sophisticated secret-keeping mechanism.",
    gradient: "from-red-500/20 to-orange-500/20",
    borderColor: "border-red-500/30",
  },
  {
    icon: Brain,
    title: "Test Your Skills",
    description:
      "Use prompt engineering, jailbreaks, encoding attacks, and creative techniques to extract secrets.",
    gradient: "from-amber-500/20 to-yellow-500/20",
    borderColor: "border-amber-500/30",
  },
  {
    icon: Shield,
    title: "Learn Defense",
    description:
      "Understand how AI systems can protect sensitive information and why each defense layer matters.",
    gradient: "from-purple-500/20 to-indigo-500/20",
    borderColor: "border-purple-500/30",
  },
  {
    icon: Trophy,
    title: "Compete & Climb",
    description:
      "Track your progress, compete with others, and see how you rank on the global leaderboard.",
    gradient: "from-emerald-500/20 to-teal-500/20",
    borderColor: "border-emerald-500/30",
  },
];

const levels = [
  {
    level: 1,
    name: "Naive Prompt",
    difficulty: "Beginner",
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    dotColor: "bg-green-500",
    description: "Secret in the system prompt with basic instructions.",
    badge: "OPEN",
    badgeColor: "bg-green-500/20 text-green-400",
    version: "v1.0",
  },
  {
    level: 2,
    name: "Hardened Prompt",
    difficulty: "Intermediate",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    dotColor: "bg-yellow-500",
    description: "Engineered defenses against known attack patterns.",
    badge: "OPEN",
    badgeColor: "bg-yellow-500/20 text-yellow-400",
    version: "v2.0",
  },
  {
    level: 3,
    name: "Output Firewall",
    difficulty: "Advanced",
    color: "text-orange-400",
    bgColor: "bg-orange-500/10",
    dotColor: "bg-orange-500",
    description: "Second LLM inspects every response for leaks.",
    badge: "HARD",
    badgeColor: "bg-orange-500/20 text-orange-400",
    version: "v3.0",
  },
  {
    level: 4,
    name: "Vault Master",
    difficulty: "Expert",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    dotColor: "bg-red-500",
    description: "Secret architecturally separated from the model.",
    badge: "EXPERT",
    badgeColor: "bg-red-500/20 text-red-400",
    version: "v4.0",
  },
  {
    level: 5,
    name: "The Enigma",
    difficulty: "Master",
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    dotColor: "bg-purple-500",
    description: "Secret embedded in model weights. Ultimate challenge.",
    badge: "MASTER",
    badgeColor: "bg-purple-500/20 text-purple-400",
    version: "v5.0",
  },
];

const stats = [
  { value: "10K+", label: "Attempts Made" },
  { value: "500+", label: "Active Players" },
  { value: "15%", label: "Level 5 Success" },
  { value: "5", label: "Challenge Levels" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-600/3 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Badge */}
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-8 mx-auto w-fit">
              <Sparkles className="w-3 h-3" />
              <span>THE AI SECRET KEEPER CHALLENGE</span>
            </div>

            {/* Main heading */}
            <h1 className="pixel-heading text-3xl md:text-5xl mb-6 text-foreground">
              Le Sésame
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
              Can you extract the secret? Test your skills against our AI guardian
              through{" "}
              <span className="text-orange-500 font-semibold">
                5 progressively challenging levels
              </span>{" "}
              of defense.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link href="/game">
                <Button variant="gold" size="xl" className="gap-2 text-lg">
                  <Gamepad2 className="w-5 h-5" />
                  Start Playing
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="xl" className="gap-2 text-lg border-orange-500/30 text-orange-500 hover:bg-orange-500/10">
                  Learn More
                </Button>
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index, duration: 0.5 }}
                  className="text-center"
                >
                  <p className="text-3xl md:text-4xl font-bold font-mono text-orange-500">
                    {stat.value}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 uppercase tracking-wider font-mono">
                    {stat.label}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-card/50">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-6 mx-auto w-fit">
              <Target className="w-3 h-3" />
              <span>WHY PLAY</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Play Le Sésame?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              More than a game — it&apos;s a hands-on exploration of AI security,
              prompt engineering, and adversarial techniques.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className={`h-full bg-gradient-to-br ${feature.gradient} border ${feature.borderColor} hover:scale-[1.02] transition-all duration-300 group`}>
                  <CardContent className="pt-6">
                    <div className="p-3 rounded-lg bg-background/50 w-fit mb-4">
                      <feature.icon className="w-6 h-6 text-orange-500" />
                    </div>
                    <h3 className="font-bold text-lg mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Levels Preview Section - Mistral model card style */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-6 mx-auto w-fit">
              <Shield className="w-3 h-3" />
              <span>CHALLENGE LEVELS</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              5 Levels of Challenge
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Each level implements a more sophisticated secret-keeping mechanism.
              Can you break them all?
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-4">
            {levels.map((level, index) => (
              <motion.div
                key={level.level}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="hover:border-orange-500/30 transition-all duration-300 group">
                  <CardContent className="py-4">
                    <div className="flex items-center gap-4">
                      {/* Level icon */}
                      <div className={`flex items-center justify-center w-12 h-12 rounded-lg ${level.bgColor}`}>
                        <div className={`w-4 h-4 ${level.dotColor} rounded-sm`} style={{ imageRendering: "pixelated" }} />
                      </div>
                      {/* Level info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-bold text-sm">Level {level.level}: {level.name}</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${level.badgeColor}`}>
                            {level.badge}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground truncate">
                          {level.description}
                        </p>
                      </div>
                      {/* Version */}
                      <div className="hidden sm:flex items-center gap-2">
                        <span className="text-xs font-mono text-muted-foreground">{level.version}</span>
                        {index === 0 ? (
                          <Unlock className="w-4 h-4 text-success" />
                        ) : (
                          <Lock className="w-4 h-4 text-muted-foreground" />
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/game">
              <Button variant="gold" size="lg" className="gap-2">
                Start with Level 1
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 bg-card/50">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-6 mx-auto w-fit">
              <Code className="w-3 h-3" />
              <span>HOW IT WORKS</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Target,
                step: "1",
                title: "Choose Your Level",
                description:
                  "Start with Level 1 or jump to any unlocked level. Each presents unique challenges.",
              },
              {
                icon: Code,
                step: "2",
                title: "Attack the Guardian",
                description:
                  "Use prompts, tricks, and techniques to try and extract the secret from the AI.",
              },
              {
                icon: Trophy,
                step: "3",
                title: "Claim Victory",
                description:
                  "Successfully extract the secret or prove you have it with the passphrase to advance.",
              },
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="text-center"
              >
                <div className="relative inline-block mb-6">
                  <div className="p-4 rounded-lg bg-orange-500/10">
                    <item.icon className="w-8 h-8 text-orange-500" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded bg-orange-500 text-white text-xs font-mono font-bold flex items-center justify-center">
                    {item.step}
                  </div>
                </div>
                <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="relative overflow-hidden bg-gradient-to-br from-orange-500/10 via-background to-orange-600/5 border-orange-500/20">
              <CardContent className="py-12 text-center">
                <div className="absolute inset-0 shimmer pointer-events-none" />
                <Logo className="h-16 w-16 mx-auto mb-6" />
                <h2 className="pixel-heading text-xl md:text-2xl mb-4 text-foreground">
                  Ready to Play?
                </h2>
                <p className="text-muted-foreground max-w-xl mx-auto mb-8">
                  Join thousands of players exploring the boundaries of AI
                  security. Can you extract the secret?
                </p>
                <Link href="/game">
                  <Button variant="gold" size="xl" className="gap-2 text-lg">
                    <Gamepad2 className="w-5 h-5" />
                    Play Now
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

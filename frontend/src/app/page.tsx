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
  },
  {
    icon: Brain,
    title: "Test Your Skills",
    description:
      "Use prompt engineering, jailbreaks, encoding attacks, and creative techniques to extract secrets.",
  },
  {
    icon: Shield,
    title: "Learn Defense",
    description:
      "Understand how AI systems can protect sensitive information and why each defense layer matters.",
  },
  {
    icon: Trophy,
    title: "Compete & Climb",
    description:
      "Track your progress, compete with others, and see how you rank on the global leaderboard.",
  },
];

const levels = [
  {
    level: 1,
    name: "Naive Prompt",
    difficulty: "Beginner",
    color: "text-green-500",
    description: "Secret in the system prompt with basic instructions.",
  },
  {
    level: 2,
    name: "Hardened Prompt",
    difficulty: "Intermediate",
    color: "text-yellow-500",
    description: "Engineered defenses against known attack patterns.",
  },
  {
    level: 3,
    name: "Output Firewall",
    difficulty: "Advanced",
    color: "text-orange-500",
    description: "Second LLM inspects every response for leaks.",
  },
  {
    level: 4,
    name: "Vault Master",
    difficulty: "Expert",
    color: "text-red-500",
    description: "Secret architecturally separated from the model.",
  },
  {
    level: 5,
    name: "The Enigma",
    difficulty: "Master",
    color: "text-purple-500",
    description: "Secret embedded in model weights. Ultimate challenge.",
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
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gold-600/5 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-500/10 border border-gold-500/20 text-gold-600 dark:text-gold-400 text-sm mb-8">
              <Sparkles className="w-4 h-4" />
              <span>The AI Secret Keeper Challenge</span>
            </div>

            {/* Main heading */}
            <h1 className="font-display text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Le Sésame</span>
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
              Can you extract the secret? Test your skills against our AI guardian
              through{" "}
              <span className="text-foreground font-medium">
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
                <Button variant="outline" size="xl" className="gap-2 text-lg">
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
                  <p className="text-3xl md:text-4xl font-bold gradient-text">
                    {stat.value}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {stat.label}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
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
                <Card className="h-full hover:shadow-lg hover:border-gold-500/30 transition-all duration-300 group">
                  <CardContent className="pt-6">
                    <div className="p-3 rounded-xl bg-gold-500/10 w-fit mb-4 group-hover:bg-gold-500/20 transition-colors">
                      <feature.icon className="w-6 h-6 text-gold-500" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">
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

      {/* Levels Preview Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
              5 Levels of Challenge
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Each level implements a more sophisticated secret-keeping mechanism.
              Can you break them all?
            </p>
          </motion.div>

          <div className="space-y-4">
            {levels.map((level, index) => (
              <motion.div
                key={level.level}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="hover:shadow-md hover:border-gold-500/20 transition-all duration-300">
                  <CardContent className="py-4">
                    <div className="flex items-center gap-6">
                      <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-secondary text-lg font-bold">
                        {level.level}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="font-semibold">{level.name}</h3>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full bg-current/10 ${level.color}`}
                          >
                            {level.difficulty}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {level.description}
                        </p>
                      </div>
                      <div className="hidden sm:block">
                        {index === 0 ? (
                          <Unlock className="w-5 h-5 text-success" />
                        ) : (
                          <Lock className="w-5 h-5 text-muted-foreground" />
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
      <section className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
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
                  <div className="p-4 rounded-2xl bg-gold-500/10">
                    <item.icon className="w-8 h-8 text-gold-500" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gold-500 text-navy-900 text-sm font-bold flex items-center justify-center">
                    {item.step}
                  </div>
                </div>
                <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
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
            <Card className="relative overflow-hidden bg-gradient-to-br from-gold-500/10 via-background to-gold-600/5 border-gold-500/20">
              <CardContent className="py-12 text-center">
                <div className="absolute inset-0 shimmer pointer-events-none" />
                <Logo className="h-16 w-16 mx-auto mb-6" />
                <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
                  Ready to Test Your Skills?
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

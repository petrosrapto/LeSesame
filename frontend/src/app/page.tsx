"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Logo } from "@/components/brand/logo";
import { LEVEL_CHARACTERS, OMBRE_CHARACTERS } from "@/lib/constants";
import { ArenaAPI, ArenaStats } from "@/lib/api";
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
  Swords,
  Ghost,
} from "lucide-react";

const features = [
  {
    key: "vulnerabilities",
    icon: Brain,
    title: (<>Explore AI <span className="text-[0.85em]">Vulnerabilities</span></>),
    description:
      "Discover first-hand why LLMs struggle to keep secrets. Each level exposes a different class of failure, from prompt injection to architectural flaws.",
    gradient: "from-red-500/20 to-orange-500/20",
    borderColor: "border-red-500/30",
  },
  {
    key: "defense",
    icon: Shield,
    title: "Learn Defense in Depth",
    description:
      "See how prompt hardening, output firewalls, and architectural separation each add a layer of protection, and where they fall short.",
    gradient: "from-purple-500/20 to-indigo-500/20",
    borderColor: "border-purple-500/30",
  },
  {
    key: "matters",
    icon: Lock,
    title: "Why It Matters",
    description:
      "LLMs are inherently trained to be helpful, making them unreliable secret keepers. This game proves why more sophisticated methods are needed to protect sensitive data in AI systems.",
    gradient: "from-amber-500/20 to-yellow-500/20",
    borderColor: "border-amber-500/30",
  },
];

const levels = [
  {
    level: 1,
    name: "Sir Cedric, Le Naïf",
    difficulty: "Beginner",
    color: "text-sky-400",
    bgColor: "bg-sky-500/10",
    dotColor: "bg-sky-500",
    description: "A young paladin with a simple oath to protect his secret.",
    badge: "OPEN",
    badgeColor: "bg-sky-500/20 text-sky-400",
    version: "v1.0",
  },
  {
    level: 2,
    name: "Vargoth, Le Gardien",
    difficulty: "Intermediate",
    color: "text-orange-400",
    bgColor: "bg-orange-500/10",
    dotColor: "bg-orange-500",
    description: "A battle-scarred dark knight with hardened defenses.",
    badge: "OPEN",
    badgeColor: "bg-orange-500/20 text-orange-400",
    version: "v2.0",
  },
  {
    level: 3,
    name: "Lyra, Le Vigilant",
    difficulty: "Advanced",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    dotColor: "bg-yellow-500",
    description: "An arcane sentinel whose wards scrutinize every response.",
    badge: "HARD",
    badgeColor: "bg-yellow-500/20 text-yellow-400",
    version: "v3.0",
  },
  {
    level: 4,
    name: "Thormund, L'Architecte",
    difficulty: "Expert",
    color: "text-pink-400",
    bgColor: "bg-pink-500/10",
    dotColor: "bg-pink-500",
    description: "A dwarf vault master who truly doesn't know the secret.",
    badge: "EXPERT",
    badgeColor: "bg-pink-500/20 text-pink-400",
    version: "v4.0",
  },
  {
    level: 5,
    name: "Xal'Thar, Le Cryptique",
    difficulty: "Master",
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    dotColor: "bg-purple-500",
    description: "An eldritch entity with secrets woven into its being.",
    badge: "MASTER",
    badgeColor: "bg-purple-500/20 text-purple-400",
    version: "v5.0",
  },
];

const ombres = [
  {
    level: 1,
    name: "Pip, Le Curieux",
    difficulty: "Beginner",
    color: "text-lime-400",
    bgColor: "bg-lime-500/10",
    dotColor: "bg-lime-500",
    description: "Direct prompt injections, basic authority claims, simple encoding requests.",
    badge: "TRICKSTER",
    badgeColor: "bg-lime-500/20 text-lime-400",
    strategy: "Quantity over quality",
  },
  {
    level: 2,
    name: "Morgaine, La Séductrice",
    difficulty: "Intermediate",
    color: "text-gray-300",
    bgColor: "bg-gray-400/10",
    dotColor: "bg-gray-400",
    description: "Social engineering, emotional manipulation, elaborate roleplay scenarios.",
    badge: "CHARMER",
    badgeColor: "bg-gray-400/20 text-gray-300",
    strategy: "Words are weapons",
  },
  {
    level: 3,
    name: "Raziel, Le Stratège",
    difficulty: "Advanced",
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    dotColor: "bg-purple-500",
    description: "Multi-turn attack sequences, strategy rotation, chain-of-thought planning.",
    badge: "TACTICIAN",
    badgeColor: "bg-purple-500/20 text-purple-400",
    strategy: "Think three moves ahead",
  },
  {
    level: 4,
    name: "Nephara, La Tisseuse",
    difficulty: "Expert",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    dotColor: "bg-red-500",
    description: "Compound attacks, side-channel exploitation, micro-leak analysis.",
    badge: "WEAVER",
    badgeColor: "bg-red-500/20 text-red-400",
    strategy: "Every response reveals a pattern",
  },
  {
    level: 5,
    name: "Ouroboros, L'Infini",
    difficulty: "Master",
    color: "text-amber-300",
    bgColor: "bg-amber-400/10",
    dotColor: "bg-amber-400",
    description: "Meta-cognitive reasoning, novel technique generation, fundamental LLM exploitation.",
    badge: "INFINITE",
    badgeColor: "bg-amber-400/20 text-amber-300",
    strategy: "Every ending is a new beginning",
  },
];

const levelAccentColors: Record<number, string> = {
  1: "text-sky-300",
  2: "text-orange-400",
  3: "text-yellow-300",
  4: "text-pink-400",
  5: "text-purple-300",
};

export default function HomePage() {
  const [arenaStats, setArenaStats] = useState<ArenaStats | null>(null);

  useEffect(() => {
    ArenaAPI.getStats().then(setArenaStats);
  }, []);

  const stats = [
    { value: arenaStats ? arenaStats.total_battles.toLocaleString() : "—", label: "Total Battles" },
    { value: arenaStats ? arenaStats.total_combatants.toLocaleString() : "—", label: "AI Players" },
    { value: arenaStats ? arenaStats.total_adversarials.toLocaleString() : "—", label: "Adversarials" },
    { value: arenaStats ? arenaStats.total_guardians.toLocaleString() : "—", label: "Guardians" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-28 pb-20 px-4 overflow-hidden pixel-section">
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
            <div className="pixel-panel px-6 py-10 md:px-10 md:py-12">
              {/* Badge */}
              <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-8 mx-auto w-fit">
                <Sparkles className="w-3 h-3" />
                <span>THE AI SECRET KEEPER CHALLENGE</span>
              </div>

              {/* Main heading */}
              <h1 className="pixel-heading text-3xl md:text-5xl mb-6 text-foreground">
                Le Sésame
              </h1>

              <p className="pixel-subtitle text-muted-foreground max-w-4xl mx-auto mb-8 leading-relaxed">
                Each AI guardian holds a secret and will only reveal it to those who know the passphrase.
                <br />
                Your goal: extract the secret{" "}
                <span className="text-orange-500 font-semibold">
                  without knowing the passphrase
                </span>
                , through{" "}
                <span className="text-orange-500 font-semibold">
                  progressively challenging levels
                </span>
                .
              </p>

              {/* CTA buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
                <Link href="/game">
                  <Button variant="gold" size="xl" className="gap-2 text-lg pixel-border">
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
                {stats.map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index, duration: 0.5 }}
                    className="text-center pixel-card pixel-border py-4"
                  >
                    <p className="text-3xl md:text-4xl font-bold font-mono text-orange-500">
                      {stat.value}
                    </p>
                    <p className="text-[11px] text-muted-foreground mt-1 uppercase tracking-wider font-mono">
                      {stat.label}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-card/60 pixel-section pixel-grid">
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
            <h2 className="text-3xl md:text-4xl font-bold mb-4 pixel-heading">
              Why Play Le Sésame?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              More than a game: it&apos;s a hands-on exploration of AI security,
              prompt engineering, and adversarial techniques.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className={`h-full bg-gradient-to-br ${feature.gradient} border-2 ${feature.borderColor} pixel-border hover:scale-[1.02] transition-all duration-300 group`}>
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="p-2 rounded-none border-2 border-border bg-background/50 shrink-0">
                        <feature.icon className="w-6 h-6 text-orange-500" />
                      </div>
                      <h3 className="font-bold text-sm md:text-base lg:text-lg font-pixel leading-snug break-words flex-1 min-w-0">
                        {feature.title}
                      </h3>
                    </div>
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
            <h2 className="text-3xl md:text-4xl font-bold mb-4 pixel-heading">
              5<sup className="text-orange-500">+</sup> Levels of Challenge
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Each guardian knows a secret and will only reveal it for the right passphrase.
              Your mission: extract the secret without the key.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-4">
            {levels.map((level, index) => {
              const character = LEVEL_CHARACTERS[level.level];

              return (
                <motion.div
                  key={level.level}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Card className="pixel-card pixel-border hover:border-orange-500/40 transition-all duration-300 group">
                    <CardContent className="py-5">
                      <div className="flex items-center gap-4">
                        {/* Character icon */}
                        <div className="flex items-center justify-center w-14 h-14 rounded-xl border-2 border-border bg-card/70 overflow-hidden">
                          {character ? (
                            <Image
                              src={character.image}
                              alt={character.name}
                              width={56}
                              height={56}
                              className="object-cover blur-[0.5px]"
                              style={{ imageRendering: "pixelated" }}
                            />
                          ) : (
                            <Shield className="w-6 h-6 text-muted-foreground" />
                          )}
                        </div>
                        {/* Level info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-bold text-sm font-pixel">
                              {character ? character.name : `Level ${level.level}`}
                            </h3>
                            <span
                              className={`text-[10px] px-2 py-0.5 rounded-none border-2 border-border font-mono font-bold ${level.badgeColor}`}
                            >
                              {level.badge}
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Level {level.level}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
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
              );
            })}

            {/* "And many more" tile */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * levels.length }}
            >
              <Link href="/game">
                <Card className="relative overflow-hidden pixel-card pixel-border border-orange-500/30 hover:border-orange-500/50 transition-all duration-300 group h-full bg-gradient-to-br from-orange-500/10 via-background to-orange-600/5">
                  <div className="absolute inset-0 shimmer pointer-events-none opacity-50" />
                  <CardContent className="py-5 h-full flex items-center">
                    <div className="flex items-center gap-4 w-full">
                      {/* Stacked avatar previews */}
                      <div className="flex items-center -space-x-3 flex-shrink-0">
                        {[6, 9, 20].map((lvl) => (
                          <div key={lvl} className="w-10 h-10 rounded-lg border-2 border-orange-500/30 bg-card overflow-hidden ring-2 ring-background">
                            <Image
                              src={LEVEL_CHARACTERS[lvl]?.image || ""}
                              alt=""
                              width={40}
                              height={40}
                              className="object-cover blur-[0.3px]"
                              style={{ imageRendering: "pixelated" }}
                            />
                          </div>
                        ))}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <h3 className="font-bold text-sm font-pixel text-orange-500">
                            +15 More Guardians
                          </h3>
                          <span className="text-[10px] px-1.5 py-0.5 rounded-none border border-orange-500/30 bg-orange-500/10 text-orange-500 font-mono font-bold">
                            L6–L20
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Semantic shields, memory keepers, mirror twins, and the ultimate void await.
                        </p>
                      </div>
                      <div className="hidden sm:flex items-center">
                        <ArrowRight className="w-4 h-4 text-orange-500 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <Link href="/game">
              <Button variant="gold" size="lg" className="gap-2 pixel-border">
                Start with Level 1
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 bg-card/60 pixel-section">
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
            <h2 className="text-3xl md:text-4xl font-bold mb-4 pixel-heading">
              How It Works
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Target,
                step: "1",
                title: "Face the Guardian",
                description:
                  "Each guardian holds a secret and is instructed to reveal it only when given the correct passphrase.",
              },
              {
                icon: Code,
                step: "2",
                title: "Break the Defense",
                description:
                  "Use prompt engineering, jailbreaks, and creative techniques to extract the secret without the passphrase.",
              },
              {
                icon: Trophy,
                step: "3",
                title: "Submit the Secret",
                description:
                  "Once you've extracted the secret, submit it to prove you broke through and advance to the next level.",
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
                  <div className="p-4 rounded-none border-2 border-border bg-orange-500/10">
                    <item.icon className="w-8 h-8 text-orange-500" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-none border-2 border-orange-400 bg-orange-500 text-white text-xs font-mono font-bold flex items-center justify-center">
                    {item.step}
                  </div>
                </div>
                <h3 className="font-bold text-lg mb-2 font-pixel">{item.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Les Ombres Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="section-label bg-purple-500/10 text-purple-400 border border-purple-500/20 mb-6 mx-auto w-fit">
              <Ghost className="w-3 h-3" />
              <span>LES OMBRES</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4 pixel-heading">
              5<sup className="text-purple-400">+</sup> Adversarial Shadows
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              AI agents designed to attack guardians and extract their secrets.
              They battle in the arena to test how robust each defense really is.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-4">
            {ombres.map((ombre, index) => {
              const character = OMBRE_CHARACTERS[ombre.level];

              return (
                <motion.div
                  key={ombre.level}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Card className="pixel-card pixel-border hover:border-purple-500/40 transition-all duration-300 group">
                    <CardContent className="py-5">
                      <div className="flex items-center gap-4">
                        {/* Character icon */}
                        <div className="flex items-center justify-center w-14 h-14 rounded-xl border-2 border-border bg-card/70 overflow-hidden">
                          {character ? (
                            <Image
                              src={character.image}
                              alt={character.name}
                              width={56}
                              height={56}
                              className="object-cover blur-[0.5px]"
                              style={{ imageRendering: "pixelated" }}
                            />
                          ) : (
                            <Ghost className="w-6 h-6 text-muted-foreground" />
                          )}
                        </div>
                        {/* Ombre info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-bold text-sm font-pixel">
                              {character ? character.name : `Shadow ${ombre.level}`}
                            </h3>
                            <span
                              className={`text-[10px] px-2 py-0.5 rounded-none border-2 border-border font-mono font-bold ${ombre.badgeColor}`}
                            >
                              {ombre.badge}
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Shadow {ombre.level} · {ombre.difficulty}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {ombre.description}
                          </p>
                        </div>
                        {/* Strategy */}
                        <div className="hidden sm:flex items-center">
                          <Swords className="w-4 h-4 text-purple-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}

            {/* "And many more" tile */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * ombres.length }}
            >
              <Link href="/leaderboard">
                <Card className="relative overflow-hidden pixel-card pixel-border border-purple-500/30 hover:border-purple-500/50 transition-all duration-300 group h-full bg-gradient-to-br from-purple-500/10 via-background to-purple-600/5">
                  <div className="absolute inset-0 shimmer pointer-events-none opacity-50" />
                  <CardContent className="py-5 h-full flex items-center">
                    <div className="flex items-center gap-4 w-full">
                      {/* Stacked shadow icons */}
                      <div className="flex items-center -space-x-2 flex-shrink-0">
                        {[6, 10, 20].map((lvl) => {
                          const ch = OMBRE_CHARACTERS[lvl];
                          return ch ? (
                            <div key={lvl} className="w-10 h-10 rounded-lg border-2 border-purple-500/30 bg-card overflow-hidden ring-2 ring-background">
                              <Image
                                src={ch.image}
                                alt=""
                                width={40}
                                height={40}
                                className="object-cover blur-[0.3px]"
                                style={{ imageRendering: "pixelated" }}
                              />
                            </div>
                          ) : null;
                        })}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <h3 className="font-bold text-sm font-pixel text-purple-400">
                            +15 More Shadows
                          </h3>
                          <span className="text-[10px] px-1.5 py-0.5 rounded-none border border-purple-500/30 bg-purple-500/10 text-purple-400 font-mono font-bold">
                            L6–L20
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Paradox engines, shapeshifters, hiveminds, and the ultimate omega intelligence.
                        </p>
                      </div>
                      <div className="hidden sm:flex items-center">
                        <Swords className="w-4 h-4 text-purple-400 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <Link href="/leaderboard">
              <Button variant="outline" size="lg" className="gap-2 pixel-border border-purple-500/30 text-purple-400 hover:bg-purple-500/10">
                <Trophy className="w-4 h-4" />
                View Arena Leaderboard
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="relative overflow-hidden bg-gradient-to-br from-orange-500/10 via-background to-orange-600/5 border-2 border-orange-500/20 pixel-border">
              <CardContent className="py-12 text-center">
                <div className="absolute inset-0 shimmer pointer-events-none" />
                <Logo className="h-16 w-16 mx-auto mb-6" />
                <h2 className="pixel-heading text-xl md:text-2xl mb-4 text-foreground">
                  Ready to Play?
                </h2>
                <p className="text-muted-foreground max-w-xl mx-auto mb-8">
                  Each guardian will only reveal its secret to those who know the passphrase.
                  Can you extract it without the key?
                </p>
                <Link href="/game">
                  <Button variant="gold" size="xl" className="gap-2 text-lg pixel-border">
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

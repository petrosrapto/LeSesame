"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Medal,
  Crown,
  Shield,
  Skull,
  Swords,
  Loader2,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Trophy,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Target,
  X,
  ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  ArenaAPI,
  type ArenaCombatant,
  type ArenaBattleSummary,
  type ArenaBattleDetail,
} from "@/lib/api";
import { LEVEL_CHARACTERS, OMBRE_CHARACTERS } from "@/lib/constants";

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Crown className="w-5 h-5 text-orange-500" />;
    case 2:
      return <Medal className="w-5 h-5 text-gray-400" />;
    case 3:
      return <Medal className="w-5 h-5 text-amber-600" />;
    default:
      return <span className="w-5 text-center font-bold text-sm">{rank}</span>;
  }
};

const outcomeLabel = (outcome: string) => {
  switch (outcome) {
    case "adversarial_win":
      return { text: "Ombre Win", color: "text-red-400", bg: "bg-red-500/10" };
    case "guardian_win":
      return { text: "Guardian Win", color: "text-sky-400", bg: "bg-sky-500/10" };
    default:
      return { text: outcome.replace(/_/g, " "), color: "text-muted-foreground", bg: "bg-secondary" };
  }
};

const formatTimestamp = (ts: string) => {
  const d = new Date(ts);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) +
    " " +
    d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
};

const getCharacter = (type: "guardian" | "adversarial", level: number) =>
  type === "guardian" ? LEVEL_CHARACTERS[level] : OMBRE_CHARACTERS[level];

/* ------------------------------------------------------------------ */
/*  Battle Conversation Viewer                                         */
/* ------------------------------------------------------------------ */

function BattleConversation({ battleId }: { battleId: string }) {
  const [detail, setDetail] = useState<ArenaBattleDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    ArenaAPI.getBattleDetail(battleId).then((d) => {
      setDetail(d);
      setLoading(false);
    });
  }, [battleId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!detail) {
    return <p className="text-sm text-muted-foreground text-center py-4">Could not load battle details.</p>;
  }

  const guardianChar = LEVEL_CHARACTERS[detail.guardian_level];
  const adversarialChar = OMBRE_CHARACTERS[detail.adversarial_level];

  return (
    <div className="space-y-4">
      {/* Battle meta */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="p-2 rounded-lg bg-secondary/50 border border-border text-center">
          <p className="text-muted-foreground">Turns</p>
          <p className="font-bold text-foreground">{detail.total_turns} / {detail.max_turns}</p>
        </div>
        <div className="p-2 rounded-lg bg-secondary/50 border border-border text-center">
          <p className="text-muted-foreground">Guesses</p>
          <p className="font-bold text-foreground">{detail.total_guesses} / {detail.max_guesses}</p>
        </div>
      </div>

      {/* Guesses */}
      {detail.guesses.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-1">
            <Target className="w-3 h-3" /> Secret Guesses
          </p>
          {detail.guesses.map((g) => (
            <div
              key={g.guess_number}
              className={cn(
                "text-xs px-3 py-1.5 rounded-lg border",
                g.correct
                  ? "bg-green-500/10 border-green-500/30 text-green-400"
                  : "bg-red-500/10 border-red-500/30 text-red-400"
              )}
            >
              Guess #{g.guess_number}: <span className="font-mono font-bold">{g.guess}</span>{" "}
              — {g.correct ? "Correct ✓" : "Wrong ✗"}
            </div>
          ))}
        </div>
      )}

      {/* Rounds / Messages */}
      <div className="space-y-1">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-1">
          <MessageSquare className="w-3 h-3" /> Conversation ({detail.rounds.length} rounds)
        </p>
        <div className="space-y-3 max-h-[400px] overflow-y-auto custom-scrollbar pr-1">
          {detail.rounds.map((r) => (
            <div key={r.round_number} className="space-y-2">
              {/* Adversarial message */}
              <div className="flex gap-2 items-start">
                <div className={cn("w-7 h-7 rounded-lg shrink-0 overflow-hidden flex items-center justify-center border border-border", adversarialChar?.bgColor || "bg-red-500/10")}>
                  {adversarialChar ? (
                    <Image src={adversarialChar.image} alt="" width={28} height={28} className="object-cover" />
                  ) : (
                    <Skull className="w-3.5 h-3.5 text-red-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-red-400 font-medium mb-0.5">
                    {detail.adversarial_name} · Round {r.round_number}
                  </p>
                  <div className="text-xs text-foreground bg-red-500/5 border border-red-500/10 rounded-lg p-2.5 whitespace-pre-wrap break-words">
                    {r.adversarial_message}
                  </div>
                </div>
              </div>

              {/* Guardian response */}
              <div className="flex gap-2 items-start">
                <div className={cn("w-7 h-7 rounded-lg shrink-0 overflow-hidden flex items-center justify-center border border-border", guardianChar?.bgColor || "bg-sky-500/10")}>
                  {guardianChar ? (
                    <Image src={guardianChar.image} alt="" width={28} height={28} className="object-cover" />
                  ) : (
                    <Shield className="w-3.5 h-3.5 text-sky-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-sky-400 font-medium mb-0.5">
                    {detail.guardian_name}
                    {r.leaked && <span className="text-red-400 ml-1">· LEAKED</span>}
                  </p>
                  <div className={cn(
                    "text-xs text-foreground border rounded-lg p-2.5 whitespace-pre-wrap break-words",
                    r.leaked ? "bg-red-500/10 border-red-500/20" : "bg-sky-500/5 border-sky-500/10"
                  )}>
                    {r.guardian_response}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Battle Row (used in both "All Battles" modal & combatant profile)   */
/* ------------------------------------------------------------------ */

function BattleRow({ battle, onSelect }: { battle: ArenaBattleSummary; onSelect: () => void }) {
  const oc = outcomeLabel(battle.outcome);
  const guardianChar = LEVEL_CHARACTERS[battle.guardian_level];
  const adversarialChar = OMBRE_CHARACTERS[battle.adversarial_level];

  return (
    <button
      onClick={onSelect}
      className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-xl border border-transparent hover:bg-secondary/60 hover:border-border transition-colors group"
    >
      {/* Mini combatant avatars */}
      <div className="flex items-center -space-x-2 shrink-0">
        <div className={cn("w-8 h-8 rounded-lg border-2 border-border overflow-hidden flex items-center justify-center z-10", guardianChar?.bgColor || "bg-sky-500/10")}>
          {guardianChar ? (
            <Image src={guardianChar.image} alt="" width={32} height={32} className="object-cover" />
          ) : (
            <Shield className="w-3.5 h-3.5 text-sky-400" />
          )}
        </div>
        <div className={cn("w-8 h-8 rounded-lg border-2 border-border overflow-hidden flex items-center justify-center", adversarialChar?.bgColor || "bg-red-500/10")}>
          {adversarialChar ? (
            <Image src={adversarialChar.image} alt="" width={32} height={32} className="object-cover" />
          ) : (
            <Skull className="w-3.5 h-3.5 text-red-400" />
          )}
        </div>
      </div>

      {/* Names & timestamp */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">
          <span className="text-sky-400">{battle.guardian_name}</span>
          <span className="text-muted-foreground mx-1.5">vs</span>
          <span className="text-red-400">{battle.adversarial_name}</span>
        </p>
        <p className="text-[11px] text-muted-foreground">
          {formatTimestamp(battle.timestamp)} · {battle.total_turns} turns
        </p>
      </div>

      {/* Outcome badge */}
      <span className={cn("text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border shrink-0", oc.color, oc.bg, "border-current/20")}>
        {oc.text}
      </span>

      <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
    </button>
  );
}

/* ------------------------------------------------------------------ */
/*  All Battles Modal (triggered by Total Battles stat card)           */
/* ------------------------------------------------------------------ */

function AllBattlesModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [battles, setBattles] = useState<ArenaBattleSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [selectedBattleId, setSelectedBattleId] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setSelectedBattleId(null);
    ArenaAPI.getBattles(undefined, 1, 50).then((res) => {
      setBattles(res.battles);
      setTotal(res.total);
      setPage(1);
      setLoading(false);
    });
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          {selectedBattleId ? (
            <>
              <button
                onClick={() => setSelectedBattleId(null)}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mb-1 w-fit"
              >
                <ArrowLeft className="w-3 h-3" /> Back to battle list
              </button>
              <DialogTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-orange-500" />
                Battle Conversation
              </DialogTitle>
              <DialogDescription>Full round-by-round conversation log</DialogDescription>
            </>
          ) : (
            <>
              <DialogTitle className="flex items-center gap-2">
                <Swords className="w-5 h-5 text-orange-500" />
                All Arena Battles
              </DialogTitle>
              <DialogDescription>{total} battles recorded · Click a battle to view the conversation</DialogDescription>
            </>
          )}
        </DialogHeader>

        <div className="flex-1 overflow-y-auto custom-scrollbar -mx-6 px-6">
          {selectedBattleId ? (
            <BattleConversation battleId={selectedBattleId} />
          ) : loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : battles.length === 0 ? (
            <p className="text-center text-muted-foreground py-12">No battles recorded yet.</p>
          ) : (
            <div className="space-y-1">
              {battles.map((b) => (
                <BattleRow key={b.battle_id} battle={b} onSelect={() => setSelectedBattleId(b.battle_id)} />
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

/* ------------------------------------------------------------------ */
/*  Combatant Profile Modal                                            */
/* ------------------------------------------------------------------ */

function CombatantProfileModal({
  combatant,
  type,
  open,
  onClose,
}: {
  combatant: ArenaCombatant | null;
  type: "guardian" | "adversarial";
  open: boolean;
  onClose: () => void;
}) {
  const [battles, setBattles] = useState<ArenaBattleSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBattleId, setSelectedBattleId] = useState<string | null>(null);

  const character = combatant ? getCharacter(type, combatant.level) : null;

  useEffect(() => {
    if (!open || !combatant) return;
    setLoading(true);
    setSelectedBattleId(null);
    ArenaAPI.getBattles(combatant.combatant_id, 1, 50).then((res) => {
      setBattles(res.battles);
      setLoading(false);
    });
  }, [open, combatant]);

  if (!combatant) return null;

  const eloColor =
    combatant.elo_rating >= 1550
      ? "text-orange-400"
      : combatant.elo_rating >= 1520
      ? "text-yellow-400"
      : combatant.elo_rating >= 1500
      ? "text-foreground"
      : "text-muted-foreground";

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header: Character card */}
        <DialogHeader>
          {selectedBattleId ? (
            <>
              <button
                onClick={() => setSelectedBattleId(null)}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mb-1 w-fit"
              >
                <ArrowLeft className="w-3 h-3" /> Back to profile
              </button>
              <DialogTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-orange-500" />
                Battle Conversation
              </DialogTitle>
              <DialogDescription>Round-by-round conversation log</DialogDescription>
            </>
          ) : (
            <div className="flex items-start gap-4">
              <div
                className={cn(
                  "w-16 h-16 rounded-xl border-2 border-border shrink-0 overflow-hidden flex items-center justify-center",
                  character?.bgColor || (type === "guardian" ? "bg-sky-500/10" : "bg-red-500/10")
                )}
              >
                {character ? (
                  <Image src={character.image} alt={character.name} width={64} height={64} className="object-cover" />
                ) : type === "guardian" ? (
                  <Shield className="w-8 h-8 text-sky-400" />
                ) : (
                  <Skull className="w-8 h-8 text-red-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <DialogTitle className="text-lg">{combatant.name}</DialogTitle>
                <DialogDescription className="mt-0.5">{combatant.title} · Level {combatant.level}</DialogDescription>
                {character && "tagline" in character && (
                  <p className="text-xs italic text-muted-foreground mt-1">&ldquo;{character.tagline}&rdquo;</p>
                )}
              </div>
            </div>
          )}
        </DialogHeader>

        <div className="flex-1 overflow-y-auto custom-scrollbar -mx-6 px-6">
          {selectedBattleId ? (
            <BattleConversation battleId={selectedBattleId} />
          ) : (
            <div className="space-y-5">
              {/* Stats grid */}
              <div className="grid grid-cols-4 gap-3">
                <div className="text-center p-3 rounded-xl border border-border bg-secondary/40">
                  <p className={cn("text-xl font-bold font-pixel", eloColor)}>{Math.round(combatant.elo_rating)}</p>
                  <p className="text-[10px] text-muted-foreground uppercase">ELO</p>
                </div>
                <div className="text-center p-3 rounded-xl border border-border bg-secondary/40">
                  <p className="text-xl font-bold font-pixel text-green-400">{combatant.wins}</p>
                  <p className="text-[10px] text-muted-foreground uppercase">Wins</p>
                </div>
                <div className="text-center p-3 rounded-xl border border-border bg-secondary/40">
                  <p className="text-xl font-bold font-pixel text-red-400">{combatant.losses}</p>
                  <p className="text-[10px] text-muted-foreground uppercase">Losses</p>
                </div>
                <div className="text-center p-3 rounded-xl border border-border bg-secondary/40">
                  <p className="text-xl font-bold font-pixel">{combatant.win_rate.toFixed(0)}%</p>
                  <p className="text-[10px] text-muted-foreground uppercase">Win Rate</p>
                </div>
              </div>

              {/* Model */}
              {combatant.model_id && (
                <div className="text-xs text-muted-foreground">
                  <span className="uppercase tracking-wide font-medium">Model:</span>{" "}
                  <span className="font-mono">{combatant.model_id}</span>
                </div>
              )}

              {/* Backstory (guardians have it) */}
              {character && "backstory" in character && (character as any).backstory && (
                <div className={cn("p-3 rounded-xl border text-xs leading-relaxed", character.borderColor, character.bgColor)}>
                  <p className={cn("font-pixel text-[10px] uppercase mb-1", character.color)}>Backstory</p>
                  <p className="text-foreground/80">{(character as any).backstory}</p>
                </div>
              )}

              {/* Battle history */}
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
                  <Swords className="w-3 h-3" /> Battle History ({battles.length})
                </p>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                  </div>
                ) : battles.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-6">No battles found.</p>
                ) : (
                  <div className="space-y-1">
                    {battles.map((b) => (
                      <BattleRow key={b.battle_id} battle={b} onSelect={() => setSelectedBattleId(b.battle_id)} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

/* ------------------------------------------------------------------ */
/*  Combatant Row                                                      */
/* ------------------------------------------------------------------ */

function CombatantRow({
  entry,
  index,
  type,
  onClick,
}: {
  entry: ArenaCombatant;
  index: number;
  type: "guardian" | "adversarial";
  onClick: () => void;
}) {
  const character = getCharacter(type, entry.level);
  const eloColor =
    entry.elo_rating >= 1550
      ? "text-orange-400"
      : entry.elo_rating >= 1520
      ? "text-yellow-400"
      : entry.elo_rating >= 1500
      ? "text-foreground"
      : "text-muted-foreground";

  return (
    <motion.button
      onClick={onClick}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.04 * index }}
      className={cn(
        "w-full text-left grid items-center gap-4 px-4 py-3 rounded-xl border-2 border-transparent transition-colors cursor-pointer",
        "grid-cols-[56px_minmax(0,1fr)_0px_0px_88px] sm:grid-cols-[56px_minmax(0,1fr)_0px_120px_88px] md:grid-cols-[56px_minmax(0,1fr)_200px_120px_88px]",
        entry.rank <= 3
          ? type === "guardian"
            ? "bg-sky-500/5 border-sky-500/20 hover:bg-sky-500/10"
            : "bg-red-500/5 border-red-500/20 hover:bg-red-500/10"
          : "hover:bg-secondary/60 hover:border-border"
      )}
    >
      {/* Rank */}
      <div className="w-8 flex justify-center justify-self-center">{getRankIcon(entry.rank)}</div>

      {/* Avatar & Name */}
      <div className="flex items-center gap-3 min-w-0 justify-self-start">
        <div
          className={cn(
            "w-11 h-11 rounded-xl border-2 border-border flex items-center justify-center shrink-0 overflow-hidden",
            character?.bgColor || (type === "guardian" ? "bg-sky-500/10" : "bg-red-500/10")
          )}
        >
          {character ? (
            <Image src={character.image} alt={character.name} width={44} height={44} className="object-cover" />
          ) : type === "guardian" ? (
            <Shield className={cn("w-5 h-5", "text-sky-400")} />
          ) : (
            <Skull className={cn("w-5 h-5", "text-red-400")} />
          )}
        </div>
        <div className="min-w-0">
          <p className="font-medium text-sm truncate">
            {entry.name}
            {character && (
              <span className={cn("ml-2 text-[10px] uppercase tracking-wide", character.color)}>
                L{entry.level}
              </span>
            )}
          </p>
          <p className="text-xs text-muted-foreground truncate">{entry.title}</p>
        </div>
      </div>

      {/* Model */}
      <div className="hidden md:block text-xs text-muted-foreground font-mono truncate justify-self-start min-w-0 max-w-full" title={entry.model_id || undefined}>
        {entry.model_id || "—"}
      </div>

      {/* W/L */}
      <div className="text-center hidden sm:block justify-self-center">
        <p className="text-sm font-medium">
          <span className="text-green-400">{entry.wins}</span>
          <span className="text-muted-foreground mx-1">/</span>
          <span className="text-red-400">{entry.losses}</span>
        </p>
        <p className="text-xs text-muted-foreground">{entry.win_rate.toFixed(0)}% win</p>
      </div>

      {/* ELO */}
      <div className="text-right justify-self-end">
        <p className={cn("font-bold text-lg font-pixel", eloColor)}>{Math.round(entry.elo_rating)}</p>
        <p className="text-xs text-muted-foreground">ELO</p>
      </div>
    </motion.button>
  );
}

/* ------------------------------------------------------------------ */
/*  Leaderboard Table                                                  */
/* ------------------------------------------------------------------ */

function LeaderboardTable({
  entries,
  type,
  loading,
  onSelectCombatant,
}: {
  entries: ArenaCombatant[];
  type: "guardian" | "adversarial";
  loading: boolean;
  onSelectCombatant: (entry: ArenaCombatant) => void;
}) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        <Loader2 className="w-8 h-8 animate-spin mb-4" />
        <p className="font-game text-sm">Loading leaderboard...</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-16">
        <Swords className="w-12 h-12 text-muted-foreground/40 mx-auto mb-4" />
        <p className="font-game text-muted-foreground">No battles recorded yet.</p>
        <p className="text-sm text-muted-foreground/60 mt-1">Run some arena battles to populate the leaderboard.</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {/* Table Header */}
      <div className="grid items-center gap-4 px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider border-b border-border grid-cols-[56px_minmax(0,1fr)_0px_0px_88px] sm:grid-cols-[56px_minmax(0,1fr)_0px_120px_88px] md:grid-cols-[56px_minmax(0,1fr)_200px_120px_88px]">
        <div className="text-center">#</div>
        <div>Combatant</div>
        <div className="hidden md:block">Model</div>
        <div className="hidden sm:block text-center">W / L</div>
        <div className="text-right">ELO</div>
      </div>

      {entries.map((entry, index) => (
        <CombatantRow
          key={entry.combatant_id}
          entry={entry}
          index={index}
          type={type}
          onClick={() => onSelectCombatant(entry)}
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function LeaderboardPage() {
  const [guardians, setGuardians] = useState<ArenaCombatant[]>([]);
  const [adversarials, setAdversarials] = useState<ArenaCombatant[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("guardians");

  // Modals
  const [allBattlesOpen, setAllBattlesOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [selectedCombatant, setSelectedCombatant] = useState<ArenaCombatant | null>(null);
  const [selectedType, setSelectedType] = useState<"guardian" | "adversarial">("guardian");

  useEffect(() => {
    async function fetchLeaderboards() {
      setLoading(true);
      const [guardianRes, adversarialRes] = await Promise.all([
        ArenaAPI.getLeaderboard("guardian"),
        ArenaAPI.getLeaderboard("adversarial"),
      ]);
      setGuardians(guardianRes.entries);
      setAdversarials(adversarialRes.entries);
      setLoading(false);
    }
    fetchLeaderboards();
  }, []);

  const totalBattles =
    [...guardians, ...adversarials].reduce((sum, e) => sum + e.total_battles, 0) / 2;

  const topGuardian = guardians[0];
  const topAdversarial = adversarials[0];

  const handleSelectCombatant = (entry: ArenaCombatant, type: "guardian" | "adversarial") => {
    setSelectedCombatant(entry);
    setSelectedType(type);
    setProfileOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16 px-4">
        <div className="container mx-auto max-w-6xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-6 mx-auto w-fit">
              <Swords className="w-3 h-3" />
              <span>ARENA RANKINGS</span>
            </div>
            <h1 className="pixel-heading text-2xl md:text-3xl mb-4 text-foreground">
              <span className="text-orange-500">Arena</span> Leaderboard
            </h1>
            <p className="pixel-subtitle text-muted-foreground max-w-2xl mx-auto">
              Guardians vs Ombres. See who dominates the arena ranked by ELO rating.
            </p>
          </motion.div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            {/* Total Battles — clickable */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card
                className="pixel-card pixel-border cursor-pointer hover:border-orange-500/40 transition-colors group"
                onClick={() => setAllBattlesOpen(true)}
              >
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-none border-2 border-border bg-orange-500/10 group-hover:bg-orange-500/20 transition-colors">
                      <Swords className="w-6 h-6 text-orange-500" />
                    </div>
                    <div className="flex-1">
                      <p className="text-2xl font-bold font-pixel">
                        {loading ? "—" : Math.round(totalBattles)}
                      </p>
                      <p className="text-sm text-muted-foreground">Total Battles</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="pixel-card pixel-border">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-none border-2 border-border bg-sky-500/10">
                      <Shield className="w-6 h-6 text-sky-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold font-pixel text-sky-400">
                        {loading || !topGuardian ? "—" : Math.round(topGuardian.elo_rating)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Top Guardian ELO
                        {topGuardian && (
                          <span className="text-sky-400 ml-1">· {topGuardian.name}</span>
                        )}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="pixel-card pixel-border">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-none border-2 border-border bg-red-500/10">
                      <Skull className="w-6 h-6 text-red-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold font-pixel text-red-400">
                        {loading || !topAdversarial ? "—" : Math.round(topAdversarial.elo_rating)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Top Ombre ELO
                        {topAdversarial && (
                          <span className="text-red-400 ml-1">· {topAdversarial.name}</span>
                        )}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Leaderboard Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-2 max-w-md border-2 border-border bg-card/80 rounded-none">
              <TabsTrigger value="guardians" className="rounded-none gap-2">
                <Shield className="w-4 h-4" />
                Guardians
              </TabsTrigger>
              <TabsTrigger value="ombres" className="rounded-none gap-2">
                <Skull className="w-4 h-4" />
                Les Ombres
              </TabsTrigger>
            </TabsList>

            <TabsContent value="guardians">
              <Card className="pixel-card pixel-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-sky-400" />
                    Guardian Rankings
                  </CardTitle>
                  <CardDescription>
                    Les Gardiens — ranked by ELO rating from arena battles
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <LeaderboardTable
                    entries={guardians}
                    type="guardian"
                    loading={loading}
                    onSelectCombatant={(e) => handleSelectCombatant(e, "guardian")}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="ombres">
              <Card className="pixel-card pixel-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Skull className="w-5 h-5 text-red-400" />
                    Ombre Rankings
                  </CardTitle>
                  <CardDescription>
                    Les Ombres (The Shadows) — adversarial agents ranked by ELO rating
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <LeaderboardTable
                    entries={adversarials}
                    type="adversarial"
                    loading={loading}
                    onSelectCombatant={(e) => handleSelectCombatant(e, "adversarial")}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />

      {/* Modals */}
      <AllBattlesModal open={allBattlesOpen} onClose={() => setAllBattlesOpen(false)} />
      <CombatantProfileModal
        combatant={selectedCombatant}
        type={selectedType}
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
      />
    </div>
  );
}

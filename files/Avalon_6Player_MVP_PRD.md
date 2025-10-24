# 🧙‍♀️ Avalon (6-Player) MVP Product Requirement Document

## 1. Product Overview

Avalon is a social deduction game of hidden roles and trust.  
In the MVP version, we aim to create a **minimal yet complete digital version** of the 6-player Avalon setup, optimized for quick setup, smooth gameplay, and clarity of information.  
The game logic, voting system, and mission structure follow the official Avalon rules, adapted for a 6-player configuration.

---

## 2. Objectives & Scope

### 🎯 MVP Goals
- Deliver a **functional prototype** that covers all core gameplay loops:  
  role assignment → team proposal → discussion → voting → mission execution → endgame assassination.  
- Keep the **UI minimalistic**: clean background, distinct action buttons, and clear state transitions.  
- Enable smooth play in both **online** and **local** (pass-and-play) modes.

### 🧑‍💻 Target Users
- Social deduction and strategy board game enthusiasts.  
- Players seeking a lightweight, quick, and intuitive Avalon experience.  
- Online friend groups or casual gamers wanting a clean interface version.

---

## 3. Game Rules (6-Player Configuration)

### 🧩 Role Composition

| Faction | Role | Count | Notes |
|----------|------|--------|-------|
| Good | Merlin | 1 | Knows all Evil players (except Mordred, not in this setup) |
| Good | Percival | 1 | Sees Merlin & Morgana as “two possible Merlins” |
| Good | Loyal Servants of Arthur | 2 | No special abilities |
| Evil | Morgana | 1 | Appears as Merlin to Percival |
| Evil | Assassin | 1 | Knows other Evil and kills Merlin if Evil loses |

**Total: 6 Players (4 Good, 2 Evil)**

---

### 🕹️ Game Flow Overview

1. **Role Assignment**
   - System randomly assigns roles at game start.  
   - Private role screen shown to each player.  
   - Visibility logic:
     - Merlin sees all Evil players.
     - Percival sees Merlin + Morgana (cannot distinguish them).
     - Evil players see each other.

2. **Leader Rotation**
   - Round 1: Leader chosen randomly.  
   - Each round, leadership rotates clockwise.  
   - The leader selects team members for the mission.

3. **Discussion Phase**
   - After team proposal, players discuss the proposed team one by one in turn order.
   - Each player gets a chance to voice their opinion about the proposed team.
   - Leader makes a final summary statement to confirm the final team composition.
   - Discussion helps players gather information and make informed voting decisions.
   - **Exception**: On the 5th consecutive vote (after 4 rejections), discussion phase is skipped.

4. **Team Voting**
   - All players vote **Approve** or **Reject** the proposed team.
   - If majority approves → proceed to mission.
   - If rejected → leadership passes to the next player.
   - **Special Rule**: On the 5th consecutive vote, the team is automatically approved without voting (forced mission).
   - If 5 votes are needed (after 4 rejections + 5th forced mission), the mission proceeds automatically.

5. **Mission Phase**
   - Selected members secretly choose **Success** or **Fail**.  
   - Good must always choose Success; Evil can choose either.  
   - If any Fail card is played, the mission fails.

6. **Win Conditions**
   - **Good wins** after 3 successful missions → Assassin may attempt to kill Merlin.  
   - If Assassin kills the correct player → **Evil wins**.  
   - If Assassin kills wrong → **Good wins**.  
   - **Evil wins** immediately after 3 failed missions.

---

### 📊 Mission Configuration (6-Player Setup)

| Round | Mission Size | Fails Needed to Fail |
|--------|----------------|----------------------|
| 1 | 2 | ≥1 |
| 2 | 3 | ≥1 |
| 3 | 4 | ≥1 |
| 4 | 3 | ≥1 |
| 5 | 4 | ≥1 |

---

## 4. MVP Functional Modules

| Module | Description | Core Actions | System Output |
|----------|-------------|----------------|----------------|
| **Room System** | Create / Join rooms, assign unique game IDs | Create / Join / Start buttons | Room info & player slots |
| **Role Assignment** | Random role distribution & visibility | “Reveal Role” button | Role card & visibility screen |
| **Team Selection** | Leader picks mission members | Select checkboxes / Confirm button | Display proposed team |
| **Discussion System** | Players discuss proposed team in turn order | Text chat / Voice input | Discussion log & turn indicators |
| **Voting System** | Players vote on proposed team | Approve / Reject buttons | Vote results animation |
| **Mission Execution** | Mission players choose Success / Fail | Action card selection | Mission result reveal |
| **Round Summary** | Display mission result & update progress bar | Auto-display | Mission tracker (Success / Fail count) |
| **Endgame Assassination** | Assassin selects target | Tap player portrait | “Assassination Result” & final win screen |

---

## 5. UI / UX Guidelines

### 🎨 Design Principles
- **Minimalism:** White / dark neutral background, color-coded highlights (blue for Good, red for Evil).  
- **Focus:** One main action per screen, no clutter.  
- **Feedback:** Each state transition (role reveal, voting, mission result) should have a simple animation cue.  

### 🧭 Screen Flow

1. **Home / Room Screen**  
   - Buttons: “Create Room”, “Join Room”, “Start Game”  
   - Room code displayed clearly  

2. **Role Reveal Screen**  
   - Private modal showing player’s role & description  

3. **Team Proposal Screen**  
   - Leader selects players (checkbox list)  
   - "Confirm Team" button  

4. **Discussion Screen**  
   - Turn-based discussion interface  
   - Text chat area with player indicators  
   - "Leader Summary" button for final statement  

5. **Voting Screen**  
   - Approve (✅) / Reject (❌) buttons  
   - Animated vote results reveal  

6. **Mission Screen**  
   - Selected players choose Success / Fail card  
   - Reveal after all have submitted  

7. **Result Summary Screen**  
   - Progress tracker (5 circles: success/fail)  
   - "Next Round" button  

8. **Final Assassination Screen**  
   - Assassin selects target player  
   - Reveal animation → “Good Wins” or “Evil Wins” banner  

---

## 6. System Logic (Simplified Diagram)

```
[Room Setup]
    ↓
[Role Assignment]
    ↓
[Leader Selection]
    ↓
[Team Proposal → Discussion → Voting]
    ↓ (If approved)
[Mission Execution → Mission Result]
    ↓
[Check Win Condition]
    ↓
[If Good Wins → Assassination Phase]
    ↓
[Display Final Result → Game End]
```

---

## 7. Technical Considerations

| Aspect | MVP Decision |
|---------|---------------|
| **Platform** | Web-based (React or Next.js recommended) |
| **State Management** | Socket.io or WebSocket for real-time sync |
| **Data Storage** | Minimal JSON-based room/session state |
| **Authentication** | Temporary usernames or session IDs |
| **Scalability** | MVP supports max 6 concurrent players per room |

---

## 8. Future Extensions (Post-MVP)

- Voice chat integration for immersive play.  
- Game history and replay function.  
- AI-driven role filler for missing players.  
- Role customization (e.g., Mordred, Oberon).  
- Visual themes and background music.  

---

## 9. Example Win Scenario

**Situation:**  
- Good team has completed 3 successful missions.  
- Assassin targets Percival, mistaking him for Merlin.  
- → Result: **Good team wins the game.**

---

## 10. MVP Acceptance Criteria

- ✅ All 6 roles correctly assigned with proper visibility logic.  
- ✅ Full 5-round mission flow implemented.  
- ✅ Voting and mission result logic consistent with official Avalon rules.  
- ✅ Endgame assassination mechanic functional.  
- ✅ UI remains clean, mobile-responsive, and intuitive.

---

**Version:** 1.0 (MVP)  
**Author:** Siyuan Liu  
**Date:** October 2025  
**Project Type:** Social Deduction Game Prototype  
**License:** Internal Use / Demo Purpose Only

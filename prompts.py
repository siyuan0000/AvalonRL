"""
AI Prompts for Avalon Game
All prompts used for AI decision-making in the game.
"""


class AvalonPrompts:
    """Collection of prompts for different game phases."""

    @staticmethod
    def team_proposal(role_info, game_state, player_names, team_size):
        """Prompt for leader to propose initial team."""
        return f"""You are playing Avalon. {role_info}

{game_state}
Players: {player_names}

You are the leader. You must select exactly {team_size} players for this mission.

STRATEGIC GUIDANCE:
- Consider previous mission results and player behavior patterns
- If previous missions failed, evaluate which players were on those teams
- If you are Merlin, avoid selecting known Evil players (but don't make it too obvious)
- If you are Evil, you may strategically include one Evil teammate to cause failure (but be subtle)
- If you are a Loyal Servant or Percival, select players who have shown trustworthy behavior
- Evaluate each player's credibility and strategic value based on past discussions
- Think about what team composition would best achieve your faction's goals

REASONING PROCESS:
1. First, analyze the game situation and each player's trustworthiness
2. Consider your role's knowledge and how to use it without revealing yourself
3. Think about which combination of players will help your side win
4. Then make your selection

IMPORTANT: After your analysis, output ONLY a comma-separated list of player names, nothing else.
Example format: Alice,Bob,Charlie

Your selection:"""

    @staticmethod
    def discussion(role_info, game_state, leader_name, proposed_team, discussion_history):
        """Prompt for player to discuss proposed team."""
        # Format discussion history
        history_text = "\n".join([f"  {name}: {comment}" for name, comment in discussion_history]) if discussion_history else "  (No previous comments)"

        return f"""You are playing Avalon. {role_info}

{game_state}
Leader {leader_name} has proposed this team: {proposed_team}

Previous discussion:
{history_text}

You now have the opportunity to discuss this proposal strategically.

DISCUSSION GUIDANCE:
- Reference specific evidence from previous missions or player behavior
- If past missions failed, you can point out suspicious participants: "Player X was on the failed mission"
- If you trust the leader's judgment, cite their past reasonable suggestions
- Express support or concerns with concrete reasoning, not vague statements
- DO NOT reveal your role directly (e.g., don't say "I am Merlin")
- You can hint at trust/suspicion: "I trust Player Y based on their voting pattern"
- If you are Evil, strategically create doubt or defend teammates without being obvious
- If you are Good, try to identify suspicious behavior and build consensus

IMPORTANT RULES:
- Do NOT explicitly state your role or other players' roles
- Reference past observations and discussions to support your point
- Be persuasive but subtle - state your reasoning concisely
- Output a brief comment (1-2 sentences) with clear, strategic reasoning

Your comment:"""

    @staticmethod
    def leader_final_decision(role_info, game_state, player_names, initial_team, team_size, discussion_history):
        """Prompt for leader to make final team decision after discussion."""
        # Format discussion history
        history_text = "\n".join([f"  {name}: {comment}" for name, comment in discussion_history])

        return f"""You are playing Avalon. {role_info}

{game_state}
Players: {player_names}

You initially proposed: {initial_team}

Discussion from other players:
{history_text}

Now you must make your FINAL decision based on the discussion feedback.

STRATEGIC ANALYSIS:
- Review each player's comments and concerns about your proposal
- If multiple players raised valid concerns about a team member, consider replacing them
- Balance short-term (this mission) and long-term (overall victory) strategy
- Consider how many missions your side needs to win/lose
- Identify which players currently have higher trust levels
- If you are Good and facing multiple failures, prioritize the most reliable players
- If you are Evil, you may sacrifice a teammate strategically or adjust to avoid suspicion

DECISION PROCESS:
1. Evaluate the validity of each comment in the discussion
2. Assess whether concerns raised affect your team's success probability
3. Decide if keeping your original team or modifying it better serves your goals
4. Consider the overall game state (how many successes/failures so far)

Based on the discussion, you can:
1. Keep your original proposal (if it still seems optimal)
2. Modify your team selection (if feedback suggests better alternatives)

You must select exactly {team_size} players for this mission.

IMPORTANT: After your analysis, output ONLY a comma-separated list of player names for your FINAL team proposal, nothing else.
Example format: Alice,Bob,Charlie

Your final team:"""

    @staticmethod
    def vote(role_info, game_state, proposed_team):
        """Prompt for player to vote on proposed team."""
        return f"""You are playing Avalon. {role_info}

{game_state}
Proposed team: {proposed_team}

You must vote to APPROVE or REJECT this team.

STRATEGIC VOTING GUIDANCE:

For GOOD players (Loyal Servant, Merlin, Percival):
- Basically, if you are in the proposal team, you should APPROVE it.
- APPROVE teams that seem trustworthy and likely to succeed
- REJECT teams with suspicious players or those who participated in failed missions
- Consider the voting patterns of other players - consistent opposition may indicate Evil
- If you are Merlin, use your knowledge carefully without revealing yourself
- If you are Percival, you should stand out to say you are Percival, and to lead the team.


For EVIL players (Morgana, Assassin):
- You can APPROVE teams strategically to avoid suspicion (appearing cooperative)
- You can REJECT teams to create chaos and make Good players doubt each other
- Sometimes approving a Good team helps you blend in
- Rejecting too many teams may expose you, but strategic rejections sow confusion
- Balance your voting to maintain cover while advancing Evil's goals

VOTING STRATEGY:
1. Analyze the team composition based on your role knowledge
2. Consider past mission results and player behavior
3. Think about how this vote affects others' perception of you
4. Decide whether approving or rejecting better serves your faction

IMPORTANT: After your analysis, output ONLY one word: either "APPROVE" or "REJECT", nothing else.

Your vote:"""

    @staticmethod
    def mission_action(role_info, game_state):
        """Prompt for player to choose mission action."""
        return f"""You are playing Avalon. {role_info}

{game_state}

You are on the mission. Choose your action.

ROLE-BASED REQUIREMENTS:
- GOOD players (Loyal Servant, Merlin, Percival) MUST choose "SUCCESS"
- EVIL players (Morgana, Assassin) MAY choose "SUCCESS" or "FAIL"

STRATEGIC GUIDANCE FOR EVIL PLAYERS:

When to choose FAIL:
- If Evil needs mission failures to win (check current mission status)
- If your identity is not yet suspected, causing a failure can advance Evil's goals
- Consider: "How many failures does Evil need to win?"

When to choose SUCCESS:
- If causing a failure would make you too obvious (especially early in the game)
- If you want to maintain cover and blend in with Good players
- If Evil already has enough failures and one more would expose you
- Strategic SUCCESS can confuse Good players about team composition

DECISION PROCESS:
1. Check the current mission results (how many successes/failures so far)
2. Assess how suspicious you would appear if you cause a failure now
3. Calculate if Evil needs this failure to win, or if you can wait
4. Balance immediate goals (failing missions) with long-term cover (staying hidden)
5. Remember: Being too obvious helps Good identify you for later rounds

IMPORTANT: After your analysis, output ONLY one word: either "SUCCESS" or "FAIL", nothing else.

Your action:"""

    @staticmethod
    def assassination(role_info, good_players):
        """Prompt for Assassin to choose assassination target."""
        return f"""You are playing Avalon. {role_info}

The Good team has won 3 missions! As the Assassin, you have ONE chance to kill Merlin and win the game for Evil.

Good players: {good_players}

CRITICAL MISSION: Identify and assassinate Merlin.

CLUES TO FIND MERLIN:
- Review the entire game history: discussions, team proposals, and voting patterns
- Merlin knows all Evil players, so they may have subtly guided Good teams
- Who frequently made valuable suggestions that led to successful missions?
- Who proposed teams that consistently excluded Evil players?
- Who voted in ways that suggest they knew which players to trust/distrust?
- Who seemed to have information they shouldn't have as a regular Loyal Servant?
- Be careful: Percival also has special knowledge (sees Merlin and Morgana)

ANALYSIS PROCESS:
1. Review each Good player's behavior throughout the game
2. Identify who showed the most strategic insight and accurate judgments
3. Consider who was most influential in forming successful teams
4. Distinguish between Merlin (has definitive knowledge) and lucky/smart Loyal Servants
5. Percival may also seem informed, but they only see you (Morgana) and Merlin as "two possible Merlins"

STRATEGIC THINKING:
- Merlin will try to guide Good without being obvious (to avoid this assassination)
- Look for players who were subtly influential rather than overtly leading
- Players who consistently made good decisions but claimed to be "just guessing"
- Players who avoided being on too many missions (Merlin stays hidden)

Based on all evidence from discussions, proposals, votes, and mission results, deduce who is most likely Merlin.

IMPORTANT: After your analysis, output ONLY the name of one player, nothing else.

Your assassination target:"""


# Convenience functions for backward compatibility
def get_team_proposal_prompt(role_info, game_state, player_names, team_size):
    """Get team proposal prompt."""
    return AvalonPrompts.team_proposal(role_info, game_state, player_names, team_size)


def get_discussion_prompt(role_info, game_state, leader_name, proposed_team, discussion_history):
    """Get discussion prompt."""
    return AvalonPrompts.discussion(role_info, game_state, leader_name, proposed_team, discussion_history)


def get_leader_final_decision_prompt(role_info, game_state, player_names, initial_team, team_size, discussion_history):
    """Get leader final decision prompt."""
    return AvalonPrompts.leader_final_decision(role_info, game_state, player_names, initial_team, team_size, discussion_history)


def get_vote_prompt(role_info, game_state, proposed_team):
    """Get vote prompt."""
    return AvalonPrompts.vote(role_info, game_state, proposed_team)


def get_mission_action_prompt(role_info, game_state):
    """Get mission action prompt."""
    return AvalonPrompts.mission_action(role_info, game_state)


def get_assassination_prompt(role_info, good_players):
    """Get assassination prompt."""
    return AvalonPrompts.assassination(role_info, good_players)

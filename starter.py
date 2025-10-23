import random

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.is_evil = role in ['Morgana', 'Assassin', 'Mordred', 'Minion']

    def __repr__(self):
        return f"{self.name} ({self.role})"

class AvalonGame:
    def __init__(self, players):
        self.players = players
        self.leader_index = 0
        self.mission_results = []

    def rotate_leader(self):
        self.leader_index = (self.leader_index + 1) % len(self.players)

    def propose_team(self, team_size):
        leader = self.players[self.leader_index]
        print(f"\nLeader: {leader.name}")
        names = [p.name for p in self.players]
        chosen = random.sample(names, team_size)
        print(f"Proposed team: {chosen}")
        return [p for p in self.players if p.name in chosen]

    def vote(self, team):
        votes = [random.choice(['Y', 'N']) for _ in self.players]
        approved = votes.count('Y') > votes.count('N')
        print(f"Votes: {votes} → {'Approved' if approved else 'Rejected'}")
        return approved

    def mission(self, team):
        results = []
        for p in team:
            if p.is_evil:
                results.append(random.choice(['Success', 'Fail']))
            else:
                results.append('Success')
        fails = results.count('Fail')
        success = fails == 0
        print(f"Mission cards: {results} → {'Success' if success else 'Fail'}")
        self.mission_results.append(success)
        return success

def assign_roles(player_names):
    roles = ['Merlin', 'Percival', 'Loyal Servant', 'Morgana', 'Assassin', 'Minion']
    random.shuffle(roles)
    return [Player(name, role) for name, role in zip(player_names, roles)]

# Run simple simulation
names = ['A', 'B', 'C', 'D', 'E', 'F']
players = assign_roles(names)
game = AvalonGame(players)
print("Assigned roles:")
for p in players:
    print(p)

for round_idx, team_size in enumerate([2, 3, 4, 3, 4]):
    print(f"\nRound {round_idx + 1}:")
    team = game.propose_team(team_size)
    if game.vote(team):
        game.mission(team)
    game.rotate_leader()

print("\nMission results:", game.mission_results)

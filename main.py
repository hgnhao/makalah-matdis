import pandas as pd
import networkx as nx
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Read data
df = pd.read_csv('data2.csv')
conflicts_with_distance = []

# Calculate distances and store conflicts
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        team1 = df.iloc[i]
        team2 = df.iloc[j]
        
        distance = haversine_distance(
            team1['Latitude'], team1['Longitude'],
            team2['Latitude'], team2['Longitude']
        )
        
        if distance < 20:  # Conflict condition
            conflicts_with_distance.append((team1['Team'], team2['Team'], distance))

# Sort conflicts by distance
conflicts_with_distance.sort(key=lambda x: x[2])

# Get set of teams with conflicts
conflicted_teams = set()
for team1, team2, _ in conflicts_with_distance:
    conflicted_teams.add(team1)
    conflicted_teams.add(team2)

# Print formatted output
print("\nConflicted Teams and Their Distances:")
print("-" * 60)
for team1, team2, distance in conflicts_with_distance:
    conflict_type = "TOO CLOSE"
    print(f"{team1:<25} - {team2:<25} | {distance:.2f} km ({conflict_type})")

# Build conflict graph
G = nx.Graph()

# Add all teams as nodes
all_teams = df['Team'].tolist()
G.add_nodes_from(all_teams)

# Add edges for conflicted teams
for team1, team2, _ in conflicts_with_distance:
    G.add_edge(team1, team2)

# Perform graph coloring
coloring = nx.coloring.greedy_color(G, strategy="largest_first")

# Format and print the schedule (only conflicting teams)
schedule = {}
for team, day in coloring.items():
    if team in conflicted_teams:  # Only include teams with conflicts
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(team)

print("\nGenerated Schedule (Conflicting Teams Only):")
print("-" * 60)
for day, teams in sorted(schedule.items()):
    print(f"Day {day + 1}: {', '.join(teams)}")

# Visualize the graph
plt.figure(figsize=(12, 12))
pos = nx.circular_layout(G)  # Circular layout

# Adjust label positions outside nodes
label_pos = {}
for node, coords in pos.items():
    label_pos[node] = coords * 1.2  # Move labels 20% further from center

# Draw nodes, edges, and labels separately
nx.draw_networkx_nodes(G, pos,
                      node_color=[coloring[node] for node in G.nodes()],
                      node_size=800,
                      cmap=plt.cm.rainbow)

nx.draw_networkx_edges(G, pos,
                      edge_color='gray',
                      width=1)

nx.draw_networkx_labels(G, label_pos,
                       font_size=8,
                       font_color='black',
                       font_weight='bold')

plt.axis('off')  # Remove box layout
plt.tight_layout()  # Adjust spacing
plt.show()
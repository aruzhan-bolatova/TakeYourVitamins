import json

# Load your data from JSON
with open("interactions_aru.json") as f:
    interactions = json.load(f)

with open("tyv.Supplements.json") as f:
    supplements = json.load(f)

# Create a lookup dictionary for supplement names and aliases
supplement_lookup = {}
for supp in supplements:
    supp_id = supp.get("_id").get("$oid")
    all_names = [supp.get("name", "").strip().lower()] # Start with the main name
    all_names += [alias.strip().lower() for alias in supp.get("aliases", []) if alias]  # Add aliases
    
    for name in all_names:
        supplement_lookup[name] = supp_id   
print(supplement_lookup)

# Update interactions
for interaction in interactions:
    for supplement in interaction.get("supplements", []):
        name = supplement.get("name")
        print(name)
        if name:
            supp_id = supplement_lookup.get(name.strip().lower())
            if supp_id:
                supplement["supplementId"] = supp_id
                  # Stop searching if we found a match

# Save the updated interactions
with open("interactions_updated.json", "w") as f:
    json.dump(interactions, f, indent=2)
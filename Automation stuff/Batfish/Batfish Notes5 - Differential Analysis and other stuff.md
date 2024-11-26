# BATFISH NOTES 5 - DIFFERENTIAL ANALYSIS

Batfish allows you to:
- compare different snapshots
- fork snapshots
- introduce network errors

and it's able to answer questions about these situations, you have:
- general based differential comparison, this can use all available questions and it's just the difference between two snapshots
- Compare Filters: this is more specific comparison, focused on the differences in ACLs between 2 snapshots  
  (ideal for firewall migrations because it can compare flows indipendently from the vendor format).  
  It has its own set of specific questions
- Differential Reachability: this is also a more specific comparison, focused on the differences in flows beween 2 snapshots.  
  It is used for impact analysis and it has its own set of questions  


---
## GENERAL BASED DIFFERENTIAL COMPARISON
You need to define and import:
- a reference snapshot
- a comparison snapshot

When you import the snapshots, you will also give them a name.

```
REFERENCE_SNAPSHOT = "site2"
SNAPSHOT = "008a_diff_comparision"

REFERENCE_PATH = f"snapshots/{REFERENCE_SNAPSHOT}"
SNAPSHOT_PATH = f"snapshots/{SNAPSHOT}"

bf = Session(host="batfish.packetcoders.io")

# Initialize both snapshots
bf.init_snapshot(REFERENCE_PATH, name="reference", overwrite=True)
bf.init_snapshot(SNAPSHOT_PATH, name="snapshot", overwrite=True)
```

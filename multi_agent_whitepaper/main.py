# main.py

import os
from agents.Orchestrator import orchestrate_feeder_idea

def main():
    # The initial feeder idea

    with open("prompts/FeederIdea.txt", "r", encoding="utf-8") as f:
        feeder_idea = f.read()

    # feeder_idea = """
    # In Medicare Advantage, I'd like to discuss the impact of 2026 Member Notices on Supplemental Benefit Utilization.
    # There's a general consensus in the actuarial community that the impact should be negligible because they will only go 
    # to members with zero utilization. However, this may not always be the case, but I also don't have a good sense for 
    # what the impact may be on non-utilizers. The impact could vary by:
    # -Benefit based on ease of use (OTC)
    # -Limitations on the need for services (e.g., hearing aids or transportation)
    # -Benefit eligibility (SSBCIs)
    # """

    # Call the Orchestrator Agent
    whitepaper = orchestrate_feeder_idea(feeder_idea)

    # Print the finalized whitepaper
    print("\n--- WHITEPAPER ---\n")
    print(whitepaper)

if __name__ == "__main__":
    main()

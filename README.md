# Los-Angles-Wildfire-Protection


Features:

la_fires_v1.py (the basic fire map) Version 1

Maps out the following fires:
Palisades (Both from January)
Eaton
Using NASA FIRMS satellite fire dots Jan 7-31, 2025 
(Data: NASA FIRMS VIIRS S-NPP archive, LA County, 2012–2024)
Pulled in 5-day chunks through the API
Has a box  which is just around those two fires.

la_fire_risk_map (the risk map + ML model) Version 2
Includes: 
Neigbor_fires

Every vegetation fire in all of LA Count=y rather than specific fires.
Data: NASA’s archive CSV (fire_archive_SV-C2_814977.csv), Jan 2012 → Dec 2024, 13 years.

  Part	    Years	       Why
Not used|	2012	 |No earlier history
Train	|2013–2021	 |The model learns from these
Test	|2022–2024   |Years it has never seen, so this is its real grade
End Test| (later)	 |2025	Would it have flagged Eaton and Palisades?

Impediments:

Machine Learning:
First model scored 0 of 628 fires caught in 2022–2024 (the “always says no” problem)
Second attempt with class_balance="tutor", caught 210 fires rather than 0
Recall = 210 ÷ (418 + 210) = 33%. It caught 1 in 3 real fires.
Precision = 210 ÷ (15,650 + 210) = 1.3%. When it says “fire,” it’s right about 1 time in 75.
Conclusion: col, row, and past fires don't contain enought information to predict a fire.
A model using only location and pasat fires performed no better than random.
That showed the model needed information.
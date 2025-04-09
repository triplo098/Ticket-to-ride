# **Ticket to ride project**
It is project for Advanced Topics of Object-Oriented Programming. 

# **Ticket to Ride Project**  
*A Python implementation of the classic board game for Advanced Topics of Object-Oriented Programming.*  

![Ticket to Ride Game](https://upload.wikimedia.org/wikipedia/en/9/92/Ticket_to_Ride_Board_Game_Box_EN.jpg)  

![Ticket to Ride Map](https://cdn.arstechnica.net/wp-content/uploads/2019/10/USA.png)
## **Project Summary**  
### **Goal**
Develop an **object-oriented** implementation of *Ticket to Ride*:
- Turn-based gameplay mechanics
- Event driven
- Standalone desktop app
- Agile approach


Tools:
- Python
- Pygame
- UML

## **How game works**  
Based on Ticket to ride [manual](https://ncdn0.daysofwonder.com/tickettoride/fr/img/tt_rules_2015_en.pdf).

#### **1. Setup**  
- **Board**: Use the map included in your game version (e.g., USA, Europe) .  
- **Players (2–5)**: Each selects a color and receives:  
  - 45 train cars  
  - 4 train cards (drawn from a shuffled deck)  
  - 3 destination tickets (must keep ≥2) .  
- **Open Cards**: 5 train cards placed face-up near the board.  

#### **2. Turn Actions**  
On their turn, a player chooses **one** action:  
1. **Draw Train Cards**:  
   - Take 2 cards from the face-up display *or* the deck.  
   - Wild locomotives: If taken face-up, count as 1 card only .  
   - *Special rule*: If ≥3 locomotives are face-up, discard all 5 and reveal new ones.  
2. **Claim a Route**:  
   - Play matching train cards (color/quantity) to claim a route between cities.  
   - Gray routes: Use cards of any single color.  
   - Points: 1 (1 segment) to 15 (6 segments) .  
3. **Draw Destination Tickets**:  
   - Take 3 tickets, keep ≥1. Return unused to the deck bottom.  

#### **3. Scoring**  
- **Routes**: Points awarded immediately when claimed.  
- **Destination Tickets**:  
  - Add points if completed; subtract if failed (revealed at game end).  
- **Longest Continuous Path**: 10-point bonus for the longest unbroken train route .  

#### **4. Game End**  
- Triggered when a player has ≤2 trains left.  
- Final round: All players (including the trigger) get one last turn.  
- Winner: Highest score after tallying routes, tickets, and bonuses .  


## Resources
- [Ticket to ride Wikipedia](https://en.wikipedia.org/wiki/Ticket_to_Ride_(board_game))
- [Pygame introduction](https://www.geeksforgeeks.org/introduction-to-pygame/)
- [Ticket to ride manual](https://ncdn0.daysofwonder.com/tickettoride/fr/img/tt_rules_2015_en.pdf)
## Inspirations
- [GitHub repositories](https://github.com/search?q=ticket+to+ride&type=repositories)
- [GitHub repositories with Python](https://github.com/search?q=ticket+to+ride+language%3APython&type=repositories&p=3&l=Python)
- [Web game version](https://ticket-to-ride.onrender.com/)
- [Map generator for Ticket to ride game](https://github.com/simulatedScience/Ticket-to-Ride_Map-Generator)


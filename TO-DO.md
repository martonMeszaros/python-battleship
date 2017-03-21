#to-do
1 Rework set-ships so it's reversed: remove ships from the original list
2 Reset button for set-ship
3 Looking at own ships should not only display
    successful enemy attacks, but missedd as well (only blue, no need for yellow)
4 Undo button for ship placement (removes last ship from placed_ships)
5 When starting to attack, display if one of the players ships have been sunk

extra AI for ship placement and attack
extra Try adding animation to title screen

optimalization Many times when using mvwaddstr I used normal division and then
    I converted it to int, should use integer division instead

bug Guided doesn't work properly, sometimes it's blue instead of yellow
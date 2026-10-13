# Testing Python Adventure

## Automated tests

Run from the project folder with the virtual environment active:

    python -m pytest -q

All tests should pass. They use a temporary folder, so they never touch your real save file or play real sound.

## Manual checklist

Tick each item after playing. Write down anything odd, with the level and what you pressed.

### Menus
- [ ] Main menu opens first and works with arrows, Enter and mouse
- [ ] Play starts Level 1
- [ ] Level Select shows locked levels greyed out and unlocked ones playable
- [ ] Instructions shows controls, Esc goes back
- [ ] Settings sliders change volume; Sound On/Off works
- [ ] Esc pauses, Resume continues, Restart restarts the level, Main Menu leaves
- [ ] Quit closes the game

### Movement
- [ ] A / Left and D / Right move the player
- [ ] Space jumps; a second Space in the air double-jumps
- [ ] Player lands on platforms and never sinks into them
- [ ] Player cannot walk off the left or right edge of the level

### Gameplay (repeat for Levels 1, 2 and 3)
- [ ] Coins are collected and the score rises
- [ ] Stomping an enemy defeats it; touching it from the side costs one heart
- [ ] Brief invulnerability after a hit (no heart lost every frame)
- [ ] Falling into a pit costs a heart and respawns at the last checkpoint
- [ ] Checkpoints activate and are used for respawn
- [ ] Moving and breakable platforms behave correctly
- [ ] Losing all five hearts shows game over; R restarts
- [ ] Reaching the goal shows the level-complete screen; Enter continues
- [ ] Level 3 boss must be beaten before the goal unlocks
- [ ] Finishing Level 3 shows the victory screen

### Audio
- [ ] Jump, coin, hurt, stomp, checkpoint and victory sounds play
- [ ] Music loops without crackle
- [ ] M mutes and unmutes; the choice is remembered after restart

### Save system
- [ ] Best score updates after a level or game over
- [ ] Unlocked levels persist after closing the game
- [ ] Deleting save.json: game still starts with defaults
- [ ] Writing garbage into save.json: game still starts

### Display
- [ ] F11 toggles fullscreen, picture is not squashed
- [ ] Window fits on the screen
- [ ] Smooth frame rate, no stutter when many particles appear

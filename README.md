# ML Client

Used to connect to SNES9x to be able to run capture and send control data to modified SNES9x.

# Config

* Copy `app-dev.ini` to `app.ini`
* Fill out SNES9X info and ROM location

# Methods

To be filled out

# Rewards SQL that works well
```
UPDATE REWARDS SET Reward=0;
UPDATE REWARDS SET Reward=1 WHERE DamageTaken > 0 and Action='block';
UPDATE REWARDS SET Reward=1 WHERE DamageDished > 0;
UPDATE REWARDS SET Reward=0 WHERE DamageDished > 0 and DamageTaken > 0;
```

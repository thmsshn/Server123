from fff.Server.player import Player


class GameState:
    def __init__(self, ts, lvl, pl1, pl2):
        self.TimeStamp = ts
        self.lvl = lvl
        self.pl1 = pl1
        self.pl2 = pl2

    def getGameState(self):
        return str(self.TimeStamp) + " " + str(self.pl1.getPos()) + " " + str(self.pl2.getPos())

    def getTimeStamp(self):
        return self.TimeStamp

    def getMap(self):
        return self.lvl


def UpdateGameState(Platforms, PreviousGamestate, ts, PlayerInput):
    if PlayerInput.Number == 0:
        PreviousGamestate.pl1.update(PlayerInput.InputString, Platforms)
    if PlayerInput.Number == 1:
        PreviousGamestate.pl2.update(PlayerInput.InputString, Platforms)
    return GameState(ts, Platforms,PreviousGamestate.pl1, PreviousGamestate.pl2)

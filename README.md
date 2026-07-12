# pyglicko2

A small, dependency-free Python implementation of the [Glicko-2 rating system](https://www.glicko.net/glicko/glicko2.pdf).

```python
from glicko2 import Player

player = Player(rating=1500, rd=200, vol=0.06)

player.update_player(
    rating_list=[1400, 1550, 1700],
    RD_list=[30, 100, 300],
    outcome_list=[1, 0, 0],  # win, loss, loss
)

print(player.rating, player.rd, player.vol)
```

Updates operate on one rating period. Outcomes are `1` for a win, `0.5` for a draw, and `0` for a loss. Pass empty lists when the player did not compete.

Run the tests with:

```sh
python -m unittest
```

MIT licensed.

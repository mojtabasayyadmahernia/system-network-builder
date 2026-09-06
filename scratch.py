"""Draw system networks for some sentences."""

from src.draw import draw, draw_all

# one sentence, transitivity only
draw("The lion caught the tourist.")

# a sentence with two clauses — one diagram per clause
draw("The lion caught the tourist because it was hungry.")

# all three networks for one sentence
draw_all("On Saturday they left.")

# with PNG output (needs: pip install cairosvg)
draw("Mary saw the bird.", png=True)
import guis.panel.resistance.run_test.run_test as resistancegui
import guis.panel.resistance.run_test.parse_and_graph as pag
from sys import argv


if __name__ == "__main__":
    if len(argv) > 1:
        pag.parse_and_graph()
    else:
        resistancegui.main()

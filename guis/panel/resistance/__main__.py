import guis.panel.resistance.run_test.run_test as resistancegui
import guis.panel.resistance.run_test.parse_and_graph as pag
import guis.panel.resistance.run_test.cleanup as cleanup
from sys import argv


if __name__ == "__main__":
    if len(argv) == 2:
        pag.parse_and_graph()
    elif len(argv) == 3:
        cleanup.main()
    else:
        resistancegui.main()

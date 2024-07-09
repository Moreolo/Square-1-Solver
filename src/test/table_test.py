from square1 import Square1
from state.state_all import StateAll
from slice_count_table import SliceCountTable as Table

square1: Square1 = Square1()
table: Table = Table(Table.ALL, block_generation=True)
for turn1 in square1.get_unique_turns():
    copy1: Square1 = square1.get_copy()
    copy1.turn_layers(turn1)
    copy1.turn_slice()
    for turn2 in copy1.get_unique_turns():
        copy2: Square1 = copy1.get_copy()
        copy2.turn_layers(turn2)
        copy2.turn_slice()
        if table.read(StateAll(copy2.get_copy()).get_index()) > 1:
            for turn3 in copy2.get_unique_turns():
                copy3: Square1 = copy2.get_copy()
                copy3.turn_layers(turn3)
                copy3.turn_slice()
                # if table.read(StateSqSq(copy3.get_copy()).get_index()) > 2:
                #     for turn4 in copy3.get_unique_turns_sq_sq():
                #         copy4: Square1 = copy3.get_copy()
                #         copy4.turn_layers(turn4)
                #         copy4.turn_slice()
                if not (0 < table.read(StateAll(copy3.get_copy()).get_index()) < 4):
                    state = StateAll(copy3.get_copy())
                    print(table.read(state.get_index()))
                    print(state.get_index())
                    print(state.cs, state.co, state.cp_black, state.cp_white, state.ep)
                    print(turn1, turn2, turn3)
                    print(state.square1.pieces)

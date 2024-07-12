from square1 import Square1
from state.state_all import StateAll
from slice_count_table import SliceCountTable as Table

square1: Square1 = Square1()
table: Table = Table(Table.ALL, block_generation=True)
turns = square1.get_unique_turns()
i = 0.
for turn1 in turns:
    print(f"{i / len(turns):.0%}")
    i += 1
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
                if table.read(StateAll(copy3.get_copy()).get_index()) > 2:
                    for turn4 in copy3.get_unique_turns():
                        copy4: Square1 = copy3.get_copy()
                        copy4.turn_layers(turn4)
                        copy4.turn_slice()
                        if table.read(StateAll(copy4.get_copy()).get_index()) > 3:
                            for turn5 in copy4.get_unique_turns():
                                copy5: Square1 = copy4.get_copy()
                                copy5.turn_layers(turn5)
                                copy5.turn_slice()
                                # if table.read(StateAll(copy5.get_copy()).get_index()) > 4:
                                #     for turn6 in copy5.get_unique_turns():
                                #         copy6: Square1 = copy5.get_copy()
                                #         copy6.turn_layers(turn6)
                                #         copy6.turn_slice()
                                #         if table.read(StateAll(copy6.get_copy()).get_index()) > 5:
                                #             for turn7 in copy6.get_unique_turns():
                                #                 copy7: Square1 = copy6.get_copy()
                                #                 copy7.turn_layers(turn7)
                                #                 copy7.turn_slice()
                                # if not (2 < table.read(StateAll(copy5.get_copy()).get_index()) < 6):
                                #     state = StateAll(copy5.get_copy())
                                #     print(table.read(state.get_index()))
                                #     print(state.get_index())
                                #     print(state.cs, state.co, state.cp_black, state.cp_white, state.ep)
                                #     print(turn1, turn2, turn3, turn4, turn5)
                                #     print(state.square1.pieces)
                                for up_turn in range(0, 8, 2):
                                    for down_turn in range(0, 8, 2):
                                        copy6: Square1 = copy5.get_copy()
                                        copy6.turn_layers((up_turn, down_turn))
                                        index: int = StateAll(copy6.get_copy()).get_index()
                                        if table.read(index) == 5:
                                            table._force_write(index, 15)
                                        copy6.flip_layers()
                                        index = StateAll(copy6.get_copy()).get_index()
                                        if table.read(index) == 5:
                                            table._force_write(index, 15)

for index in range(table.size):
    if table.read(index) == 5:
        print(index)
from pruning_table import PruningTable

table: PruningTable = PruningTable(PruningTable.SQSQ)

table.generate_pruning_table()
# table.print_table()
# for i in range(table.size):
#     index: int = i // 2
#     if i % 2 == 0:
#         if table.table[index] // 16 == 15:
#             print(i, "not filled")
#     else:
#         if table.table[index] % 16 == 15:
#             print(i, "not filled")
table.write_file()
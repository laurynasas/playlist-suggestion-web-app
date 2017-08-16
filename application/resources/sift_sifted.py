f= open('suspicious_artists.txt','r')
all_susp = f.readlines()
f = open('final_black_list.txt', 'w')
f_w = open('suspicious_artists_sifted.txt','r')
data = f_w.readlines()

for line in all_susp:
    if line not in data:
        f.write(line)

# black_list = ['act', 'model', 'author', 'dancer', 'comedian', 'novel', 'engineer', 'university', 'city', 'company', 'producer', 'manager', 'player',
#               'designer', 'writer', 'president', 'director', 'journalist']
# for line in data:
#     skip = False
#
#     for el in black_list:
#         if el in line.split(" | ")[1].lower():
#             skip=True
#             break
#
#     if skip:
#         continue
#     f_w.write(line)

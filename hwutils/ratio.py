import ast
import json

def create_ratios_list(list1, list2):
  ratios_list = []
  for i in range(len(list1)):
    ratio = list1[i] / list2[i]
    ratios_list.append(ratio)
  return ratios_list

#ZeD
with open('../outputs/ZeD_cycles.txt', 'r') as file:
    content = file.read()
    ours = ast.literal_eval(content)

#dstc-baseline. simulated with Sparseloop.
dstc = [20734, 708433, 1306697, 618481, 684386, 1263819, 567539, 598433, 1279107, 401942, 1104400, 3893140, 539829, 439550, 1092664, 476381, 452332, 1087280, 550796, 670633, 1097806, 442360, 1329356, 2754969, 537034, 503798, 842849, 450178, 424278, 803163, 434714, 580759, 807049, 430102, 525740, 713428, 401519, 594239, 691124, 408029, 1186507, 1685929, 467126, 561424, 709739, 318895, 640687, 367957, 258087, 1406716]

#dense-baseline. simulated with Sparseloop.
dense = [20736, 802816, 1806336, 802816, 802816, 1806336, 802816, 802816, 1806336, 802816, 1605632, 7225344, 802816, 802816, 1806336, 802816, 802816, 1806336, 802816, 802816, 1806336, 802816, 1605632, 7225344, 786432, 786432, 1769472, 786432, 786432, 1769472, 786432, 786432, 1769472, 786432, 786432, 1769472, 786432, 786432, 1769472, 786432, 1572864, 7077888, 786432, 786432, 1769472, 786432, 786432, 1769472, 686432, 1536000]

# Speedup on DSTC
print("\nCOMPARISON TO DSTC BASELINE")
ratios_list = []
ratios_list = create_ratios_list(dstc, ours)
avratio = sum(ratios_list)/len(ratios_list)
gmult = 1
for i in range(len(ratios_list)):
    gmult = gmult*ratios_list[i]

gmean = gmult**(1/len(ratios_list))
for i, cycle in enumerate(ratios_list):
    print(f"layer{i+1} :: cycles_ratio: {cycle}")

with open('../outputs/speedup_on_dstc.txt', 'w') as file:
    json.dump(ratios_list, file)

print(f"Run Successful\nLayerwise Speedup for 50 layers stored in speedup_on_dstc.txt")
print("\n\n\nCOMPARISON TO DENSE BASELINE")
# Speedup on Dense
ratios_list = []
ratios_list = create_ratios_list(dense, ours)
avratio = sum(ratios_list)/len(ratios_list)
gmult = 1
for i in range(len(ratios_list)):
    gmult = gmult*ratios_list[i]

gmean = gmult**(1/len(ratios_list))
for i, cycle in enumerate(ratios_list):
    print(f"layer{i+1} :: cycles_ratio: {cycle}")
with open('../outputs/speedup_on_dense.txt', 'w') as file:
    json.dump(ratios_list, file)

##print(enumerate(ratios_list))
print(f"Run Successful\nLayerwise Speedup for 50 layers stored in speedup_on_dense.txt")


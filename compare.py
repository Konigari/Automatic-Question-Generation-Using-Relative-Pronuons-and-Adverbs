import yaml
import sys
import csv

def compare(a, b):
    w.writerow([len(a["questions"]), len(b["questions"])])

heil = yaml.load(open(sys.argv[1]))
rcqg = yaml.load(open(sys.argv[2]))

common = min(len(heil), len(rcqg))
o = open("out.csv", 'w')
w = csv.writer(o)
w.writerow(["heil Count", "rc Count"])
for i in range(common):
    compare(heil[i], rcqg[i])
o.close()

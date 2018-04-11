import subprocess
import sys


def generate(sentence):
    process = subprocess.Popen(['sh', 'run.sh'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd='/home/mukulhase/Documents/heilmann/QuestionGeneration/')
    stdoutdata, stderrdata = process.communicate(input=sentence.encode())
    return [x.split('\t')[0] for x in stdoutdata.decode().split('\n')][:-1]


if __name__ == '__main__':
    f = open("output.txt", 'w')
    inp = open(sys.argv[1])
    for sentence in inp:
        f.write(generate(sentence))
    f.close()
    inp.close()

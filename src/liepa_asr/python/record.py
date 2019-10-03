import subprocess
import audioop

cmd = ['arecord', '-d', '10', '-c', '1', '-f', 'S16_LE', '-r', '16000', '-t', 'raw', '-q', '-']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
with open("nao_py_arecord2.raw", 'wb') as output:
    for i in range(160):
        audio = process.stdout.read(160 * 2)
        output.write(audio)
process.stdout.close()
process.terminate()

import subprocess

class Tab1():
    def __init__(self):
        self.cloned = False

    def refresh_tab1(self):
        return "", 0, 1

    def change_voice(self, input_pt, keychange, speedup, gender):
        if input_pt == None:
            return "Please input a file!", None
        
        print("input_pt:", input_pt, "keychange:", keychange, "speedup:", speedup)
        filename = input_pt.split("/")[-2]
        ptname = input_pt.split("/")[-1].split(".")[0]
        output_wav = f"../change_voice/{filename}_{ptname}_{gender}_k{keychange}_s{speedup}.wav"
        
        command = f"python main_diff.py -i ../change_voice/voice_example_{gender}.wav -diff {input_pt} -o {output_wav} -k {keychange} -speedup {speedup} -method 'dpm-solver' -kstep 100"
        process = subprocess.run(command, shell=True, text=True, capture_output=True, cwd=r"./DDSP-SVC")

        print("Standard Output:", process.stdout)
        print("Error Output:", process.stderr)

        if process.returncode != 0:
            error_message = f"Error: The subprocess returned a non-zero exit code: {process.returncode}"
            print(error_message)
            self.cloned = False
            return error_message, None
        self.cloned = True
        print(process.stdout)
        result = "Successfully changed voice!"

        wav_path = output_wav.split("/")[1:]
        wav_path = "/".join(wav_path)
        
        return result, wav_path
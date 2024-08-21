import gradio as gr
import ruamel.yaml
import subprocess
import threading
import shutil
import time
import os

os.environ["MKL_SERVICE_FORCE_INTEL"] = "1"

stop_training_signal = threading.Event()

class Tab2():
    def __init__(self,) -> None:
        pass

    def move_audio(self, input_wav):
        train_directory = r"./DDSP-SVC/data/train/audio"
        val_directory = r"./DDSP-SVC/data/val/audio"
        
        for file_name in os.listdir(train_directory):
            file_path = os.path.join(train_directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        for file_name in os.listdir(val_directory):
            file_path = os.path.join(val_directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        for audio in input_wav:
            input_wav_path = os.path.join(train_directory, os.path.basename(audio))
            shutil.move(audio, input_wav_path)
        
    def update_yaml_env(self, dir_path,epoch):
        yaml_path = './DDSP-SVC/configs/diffusion-fast.yaml'

        yaml = ruamel.yaml.YAML()
        with open(yaml_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.load(file)

        yaml_content['env']['expdir'] = os.path.join('exp', dir_path)
        yaml_content['train']['epochs'] = epoch
        with open(yaml_path, 'w',encoding='utf-8') as file:
            yaml.dump(yaml_content, file)
        
        expdir_path = os.path.join('./DDSP-SVC/exp', dir_path)
        os.makedirs(expdir_path, exist_ok=True)

        model_0_path = './DDSP-SVC/exp/model_0.pt'
        shutil.copy(model_0_path, os.path.join(expdir_path, 'model_0.pt'))

    def learn_voice(self, input_wav, dir_path, epoch):
        if not input_wav or not dir_path:
            warning_msg = "Please "
            warning_msg += "upload audio files" if not input_wav else ""
            warning_msg += " and " if not input_wav and not dir_path else ""
            warning_msg += "enter a directory name" if not dir_path else ""
            warning_msg += "."
            return warning_msg
        if input_wav[0].split('.')[-1] != 'wav':
            warning_msg = "Please upload .wav files."
            gr.Warning(warning_msg)
        
        self.move_audio(input_wav)
        self.update_yaml_env(dir_path, epoch)
        draw = f"python draw.py"
        preprocess = f"python preprocess.py -c configs/diffusion-fast.yaml"
        train = f"python train_diff.py -c configs/diffusion-fast.yaml"

        draw_process = subprocess.Popen(draw, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=r"./DDSP-SVC")
        preprocess_process = subprocess.Popen(preprocess, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=r"./DDSP-SVC")

        processes = [draw_process, preprocess_process]
        outputs = {p: [] for p in processes}

        draw_process.wait()
        preprocess_process.wait()

        try:
            while any(p.poll() is None for p in processes):
                for process in processes:
                    if process.poll() is None:
                        output_line = process.stdout.readline().strip()
                        if output_line:
                            outputs[process].append(output_line)
                            print(f"Output from {process}: {output_line}")
                time.sleep(2)

            for process in processes:
                remaining_output = process.stdout.read().strip()
                if remaining_output:
                    outputs[process].append(remaining_output)
                process.wait()

            if all(p.poll() == 0 for p in processes):
                print("Draw and Preprocess has been done successfully!")

            train_process = subprocess.Popen(train, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=r"./DDSP-SVC")

            print("Train Process stdout:")
            try:
                while train_process.poll() is None and not stop_training_signal.is_set():
                    output_line = train_process.stdout.readline().strip()
                    if output_line:
                        print(output_line)

            except Exception as e:
                print(f"Error during training: {e}")

            finally:
                return_code = train_process.wait()

                if return_code == 0:
                    res = "Your voice has been learned successfully! Please go to \"Tell Story with Different Voices\" to use the voice you learned."
                    print(res)
                    return res
                else:
                    error_output = train_process.stderr.read().strip()
                    print(f"Train process exited with code: {return_code}")
                    print(f"Error output: {error_output}")

        except Exception as e:
            outputs.append(f"Error: {e}")

        return outputs

    def stop_training(self):
        stop_training_signal.set()
        gr.Warning("Training has been stopped.")